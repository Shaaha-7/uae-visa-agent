# gov_intel/uae_visa_client.py
"""
context.dev client tailored for UAE government visa information retrieval.
Sources official/authoritative UAE government domains for visa types,
requirements, fees, and FAQs.
"""

import os
import json
import time
import requests
from typing import Optional
from dataclasses import dataclass


CONTEXT_DEV_API_BASE = "https://api.context.dev/v1"
CONTEXT_DEV_API_KEY = os.environ.get("CONTEXT_DEV_API_KEY")

# Authoritative UAE government sources — stick to these, not random blogs/agencies
UAE_OFFICIAL_SOURCES = {
    "federal_portal": "https://u.ae/en/information-and-services/visa-and-emirates-id",
    "icp": "https://icp.gov.ae/en/",  # Federal Authority for Identity, Citizenship, Customs & Port Security
    "gdrfa_dubai": "https://www.gdrfad.gov.ae/en",  # Dubai residency/visa authority
    "mofa": "https://www.mofa.gov.ae/en/",
    "emirates_id": "https://u.ae/en/information-and-services/visa-and-emirates-id/emirates-id",
    "overstay": "https://u.ae/en/information-and-services/visa-and-emirates-id/overstaying-your-visa",
    "family_sponsorship": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/residence-visa-for-family-members",
    "green_visa": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/the-green-visa",
    "work_visa": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/residence-visa-for-working-in-the-uae",
    "retirement_visa": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/retirement-visa",
}


class ContextDevError(Exception):
    pass


@dataclass
class CacheEntry:
    data: dict
    fetched_at: float


class UAEVisaIntelClient:
    """
    Fetches live UAE visa info restricted to official government sources.
    Caches aggressively since visa rules change slowly, not per-request.
    """

    def __init__(self, api_key: Optional[str] = None, cache_ttl_seconds: int = 86400, timeout: int = 60):
        self.api_key = api_key or os.environ.get("CONTEXT_DEV_API_KEY")
        if not self.api_key:
            raise ValueError("CONTEXT_DEV_API_KEY not set")
        self.cache_ttl = cache_ttl_seconds  # 24h default — visa rules don't change hourly
        self.timeout = timeout
        self.cache_file = os.path.join(os.path.dirname(__file__), "visa_cache.json")
        self._cache: dict[str, CacheEntry] = self._load_disk_cache()

    def _load_disk_cache(self) -> dict[str, CacheEntry]:
        cache = {}
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    for k, v in raw.items():
                        cache[k] = CacheEntry(data=v["data"], fetched_at=v["fetched_at"])
            except Exception as e:
                print(f"  [CACHE WARN] Could not load disk cache: {e}")
        return cache

    def _save_disk_cache(self) -> None:
        try:
            raw = {
                k: {"data": v.data, "fetched_at": v.fetched_at}
                for k, v in self._cache.items()
            }
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(raw, f, indent=2)
        except Exception as e:
            print(f"  [CACHE WARN] Could not save disk cache: {e}")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _get_cached(self, key: str) -> Optional[dict]:
        entry = self._cache.get(key)
        if entry:
            return entry.data
        for k, e in self._cache.items():
            # Nationality exact-prefix match
            if key.startswith("nationality:") and k == key:
                return e.data
            if "fines" in key and "fines" in k:
                return e.data
            if "fine" in key and "fines" in k:
                return e.data
            if "overstay" in key and "fines" in k:
                return e.data
            if "ban" in key and "fines" in k:
                return e.data
            if "penalty" in key and "fines" in k:
                return e.data
            if "employer" in key and "fines" in k:
                return e.data
            if "tourist" in key and "tourist" in k and "fines" not in key:
                return e.data
            if "golden" in key and "golden" in k:
                return e.data
            if "studying" in key and "studying" in k:
                return e.data
            if "visit" in key and "tourist" in k and "fines" not in key:
                return e.data
        return None

    def _set_cached(self, key: str, data: dict) -> None:
        self._cache[key] = CacheEntry(data=data, fetched_at=time.time())
        self._save_disk_cache()

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{CONTEXT_DEV_API_BASE}/{endpoint}"
        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            raise ContextDevError(f"context.dev timed out on {endpoint}")
        except requests.exceptions.HTTPError as e:
            raise ContextDevError(f"context.dev HTTP error on {endpoint}: {e} | Body: {resp.text}")
        except requests.exceptions.RequestException as e:
            raise ContextDevError(f"context.dev request failed on {endpoint}: {e}")

    def extract_visa_page(
        self, url: str, instructions: str, schema: Optional[dict] = None, use_cache: bool = True
    ) -> dict:
        """
        Generic extractor for any UAE gov visa page. Always pass explicit
        instructions describing exactly what fields you need — don't rely
        on the model to guess structure for legal/government content.
        """
        if schema is None:
            schema = {
                "type": "object",
                "properties": {
                    "details": {"type": "string"}
                }
            }

        cache_key = f"extract:{url}:{instructions}:{str(schema)}"
        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached

        payload = {"url": url, "instructions": instructions, "schema": schema}
        try:
            data = self._post("web/extract", payload)
            if use_cache:
                self._set_cached(cache_key, data)
            return data
        except ContextDevError as e:
            # Fallback to any cached data for this key or URL if API fails or credits run out
            for k, entry in self._cache.items():
                if url in k:
                    print(f"  [CACHE FALLBACK] Serving persistent cached data for {url}")
                    return entry.data
            raise e

    def get_visa_types_overview(self) -> dict:
        """Federal portal: list of visa types (tourist, residency, golden visa, etc.)"""
        schema = {
            "type": "object",
            "properties": {
                "visa_types": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "category": {"type": "string"},
                            "eligibility_summary": {"type": "string"},
                            "link": {"type": "string"}
                        },
                        "required": ["name"]
                    }
                }
            },
            "required": ["visa_types"]
        }
        return self.extract_visa_page(
            url=UAE_OFFICIAL_SOURCES["federal_portal"],
            instructions=(
                "Extract every visa type listed (name, category, eligibility summary). "
                "Include links to detail pages if present. Do not infer types not explicitly listed."
            ),
            schema=schema,
        )

    def get_visa_requirements(self, visa_type: str) -> dict:
        """
        Requirements + documents + fees for a specific visa type, e.g.
        'golden visa', 'tourist visa', 'work visa', 'family residency'.
        """
        schema = {
            "type": "object",
            "properties": {
                "visa_type": {"type": "string"},
                "eligibility_categories": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category_name": {"type": "string"},
                            "eligibility_requirements": {"type": "string"},
                            "validity_years": {"type": "string"}
                        },
                        "required": ["category_name"]
                    }
                },
                "general_requirements": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "validity_period": {"type": "string"}
            },
            "required": ["visa_type"]
        }
        target_url = (
            "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/golden-visa"
            if "golden" in visa_type.lower()
            else UAE_OFFICIAL_SOURCES["federal_portal"]
        )
        return self.extract_visa_page(
            url=target_url,
            instructions=(
                f"Extract all eligibility criteria, requirements, financial thresholds, required qualifications, "
                f"and validity period for '{visa_type}' across all eligible categories (e.g. real estate investors, "
                f"investors in public investments, entrepreneurs, outstanding talents, doctors/scientists, high-performing students). "
                f"Do not guess or omit any explicitly listed requirements."
            ),
            schema=schema,
        )

    def get_visa_faqs(self, topic: str) -> dict:
        """
        Pulls Q&A content specifically — e.g. topic='golden visa renewal',
        'overstay fines', 'family sponsorship'.
        """
        schema = {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "faqs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "answer": {"type": "string"}
                        },
                        "required": ["question", "answer"]
                    }
                }
            },
            "required": ["topic"]
        }
        return self.extract_visa_page(
            url=UAE_OFFICIAL_SOURCES["gdrfa_dubai"],
            instructions=(
                f"Find any FAQ, help, or Q&A content related to '{topic}'. "
                f"Extract each question and its official answer verbatim as listed. "
                f"If no FAQ content exists for this topic on this page, return an empty result — do not fabricate Q&As."
            ),
            schema=schema,
        )

    def get_visa_fees(self, visa_type: str) -> dict:
        """Fee schedule lookup — flagged separately since fees change and matter most."""
        schema = {
            "type": "object",
            "properties": {
                "visa_type": {"type": "string"},
                "fees": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "fee_description": {"type": "string"},
                            "amount_aed": {"type": "string"}
                        },
                        "required": ["fee_description"]
                    }
                },
                "page_section": {"type": "string"}
            },
            "required": ["visa_type"]
        }
        return self.extract_visa_page(
            url=UAE_OFFICIAL_SOURCES["icp"],
            instructions=(
                f"Extract only the fee amounts (in AED) associated with '{visa_type}', "
                f"including any service fees, typing fees, or Emirates ID fees mentioned. "
                f"Note the exact page section this came from."
            ),
            schema=schema,
        )

    def get_visa_processing_time(self, visa_type: str) -> dict:
        """
        Extract processing duration, timeline, and steps required for a specific visa type.
        """
        schema = {
            "type": "object",
            "properties": {
                "visa_type": {"type": "string"},
                "processing_time": {"type": "string"},
                "steps_or_requirements": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "official_note": {"type": "string"}
            },
            "required": ["visa_type"]
        }
        target_url = (
            "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/residence-visa-for-studying-in-the-uae"
            if "student" in visa_type.lower()
            else UAE_OFFICIAL_SOURCES["federal_portal"]
        )
        return self.extract_visa_page(
            url=target_url,
            instructions=(
                f"Extract the official processing time / duration required for '{visa_type}' application process. "
                f"Include any details on validity, steps, or duration if stated on the official page. "
                f"If processing time is not explicitly stated, state clearly that it is not specified — do not guess."
            ),
            schema=schema,
        )

    def smart_extract(self, query: str, target_url: Optional[str] = None) -> dict:
        """
        Dynamically selects the best target URL and builds an optimal extraction schema
        based on the user's question, avoiding rigid hardcoded URLs.
        """
        q_lower = query.lower()

        DYNAMIC_URL_MAP = {
            "tourist": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/tourist-visa",
            "visit_on_arrival": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/tourist-visa",
            "golden": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/golden-visa",
            "student": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/residence-visa-for-studying-in-the-uae",
            "work": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/residence-visa-for-working-in-the-uae",
            "green": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/the-green-visa",
            "emirates_id": "https://u.ae/en/information-and-services/visa-and-emirates-id/emirates-id",
            "overstay": "https://u.ae/en/information-and-services/visa-and-emirates-id/overstaying-your-visa",
            "fines_complete": "uae-fines-complete",
            "family": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/residence-visa-for-family-members",
            "retirement": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/retirement-visa",
            "nationality": "https://u.ae/en/information-and-services/visa-and-emirates-id/do-you-need-a-uae-visa",
            "federal_portal": "https://u.ae/en/information-and-services/visa-and-emirates-id"
        }

        # Nationality keyword map — detects country names in user question
        NATIONALITY_KEYWORDS = {
            "indian": "Indian", "india": "Indian",
            "pakistani": "Pakistani", "pakistan": "Pakistani",
            "filipino": "Filipino", "philippines": "Filipino",
            "bangladeshi": "Bangladeshi", "bangladesh": "Bangladeshi",
            "nepali": "Nepali", "nepal": "Nepali",
            "sri lankan": "Sri Lankan", "sri lanka": "Sri Lankan",
            "british": "British", "uk": "British", "united kingdom": "British",
            "american": "American", "us": "American", "united states": "American",
            "canadian": "Canadian", "canada": "Canadian",
            "australian": "Australian", "australia": "Australian",
            "chinese": "Chinese", "china": "Chinese",
            "russian": "Russian", "russia": "Russian",
            "egyptian": "Egyptian", "egypt": "Egyptian",
            "jordanian": "Jordanian", "jordan": "Jordanian",
            "lebanese": "Lebanese", "lebanon": "Lebanese",
            "nigerian": "Nigerian", "nigeria": "Nigerian",
            "kenyan": "Kenyan", "kenya": "Kenyan",
            "french": "French", "france": "French",
            "german": "German", "germany": "German",
            "iranian": "Iranian", "iran": "Iranian",
            "turkish": "Turkish", "turkey": "Turkish",
            "ethiopian": "Ethiopian", "ethiopia": "Ethiopian",
            "saudi": "Saudi Arabian", "saudi arabia": "Saudi Arabian",
            "emirati": "Emirati", "uae national": "Emirati",
        }

        detected_nationality = None
        for kw, nat in NATIONALITY_KEYWORDS.items():
            if kw in q_lower:
                detected_nationality = nat
                break

        if target_url is None:
            # 1. Nationality-specific question — live extraction from context.dev
            if detected_nationality and target_url is None:
                print(f"  [NATIONALITY] Detected nationality: {detected_nationality} — fetching live from context.dev")
                return self.get_nationality_visa_info(detected_nationality, query)

            # 2. Emirates ID
            elif "emirates id" in q_lower or "eid" in q_lower or "identity card" in q_lower or "id card" in q_lower:
                target_url = DYNAMIC_URL_MAP["emirates_id"]
            # 3. Fines / violations / bans
            elif (
                "fine" in q_lower or "penalty" in q_lower or "ban" in q_lower
                or "violation" in q_lower or "illegal" in q_lower or "absconding" in q_lower
                or "cancel visa" in q_lower or "employer" in q_lower or "without permit" in q_lower
            ):
                target_url = DYNAMIC_URL_MAP["fines_complete"]
            # 4. Overstay / expiry
            elif "overstay" in q_lower or "expire" in q_lower:
                target_url = DYNAMIC_URL_MAP["overstay"]
            # 5. Family sponsorship
            elif "family" in q_lower or "spouse" in q_lower or "wife" in q_lower or "husband" in q_lower or "dependent" in q_lower or "child" in q_lower:
                target_url = DYNAMIC_URL_MAP["family"]
            # 6. Retirement visa
            elif "retirement" in q_lower or "retire" in q_lower:
                target_url = DYNAMIC_URL_MAP["retirement"]
            # 7. Visa on arrival / airport
            elif "on arrival" in q_lower or "airport" in q_lower:
                target_url = DYNAMIC_URL_MAP["visit_on_arrival"]
            # 8. Tourist / visit
            elif "tourist" in q_lower or "visit" in q_lower:
                target_url = DYNAMIC_URL_MAP["tourist"]
            # 9. Golden Visa
            elif "golden" in q_lower:
                target_url = DYNAMIC_URL_MAP["golden"]
            # 10. Student / study
            elif "student" in q_lower or "study" in q_lower or "university" in q_lower:
                target_url = DYNAMIC_URL_MAP["student"]
            # 11. Work / employment
            elif "work" in q_lower or "job" in q_lower or "employment" in q_lower or "labour" in q_lower or "labor" in q_lower:
                target_url = DYNAMIC_URL_MAP["work"]
            # 12. Green Visa
            elif "green" in q_lower:
                target_url = DYNAMIC_URL_MAP["green"]
            else:
                target_url = DYNAMIC_URL_MAP["federal_portal"]

        schema = {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "direct_answer": {"type": "string"},
                "eligibility_criteria": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "application_steps": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "fees_or_validity": {"type": "string"}
            },
            "required": ["topic", "direct_answer"]
        }

        instructions = (
            f"Answer the user's question: '{query}'. "
            f"Extract all direct eligibility rules, nationality-specific conditions (if applicable, e.g. for Indian passport holders or visa-on-arrival), "
            f"documents required, application steps, and validity period. "
            f"Be precise and strictly reflect official government portal information."
        )

        return self.extract_visa_page(url=target_url, instructions=instructions, schema=schema)

    def get_nationality_visa_info(self, nationality: str, user_question: str = "") -> dict:
        """
        Live context.dev extraction: fetches UAE visa eligibility, entry rules,
        and requirements specifically for a given nationality from official UAE portals.
        Results are cached by nationality to avoid duplicate API calls.
        """
        cache_key = f"nationality:{nationality.lower()}"
        cached = self._get_cached(cache_key)
        if cached:
            print(f"  [NATIONALITY CACHE] Serving cached data for {nationality}")
            return cached

        schema = {
            "type": "object",
            "properties": {
                "nationality": {"type": "string"},
                "visa_requirement": {"type": "string"},
                "visa_on_arrival_eligible": {"type": "string"},
                "visa_free_duration": {"type": "string"},
                "tourist_visa_options": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "how_to_apply": {"type": "string"},
                "required_documents": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "fees_or_validity": {"type": "string"},
                "special_notes": {"type": "string"}
            },
            "required": ["nationality", "visa_requirement"]
        }

        instructions = (
            f"Extract UAE entry and visa rules specifically for {nationality} passport holders. "
            f"Include: (1) whether they need a pre-arranged visa or get visa on arrival or visa-free entry, "
            f"(2) duration of stay allowed, (3) how to apply for a UAE tourist or visit visa if required, "
            f"(4) required documents, (5) any special conditions (e.g. Indian citizens with US/UK visa get visa on arrival). "
            f"User's original question: '{user_question}'. "
            f"Be precise and only state what is officially confirmed on this page."
        )

        # Try the dedicated nationality visa check page first, then fallback to tourist visa page
        urls_to_try = [
            "https://u.ae/en/information-and-services/visa-and-emirates-id/do-you-need-a-uae-visa",
            "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/tourist-visa",
            "https://icp.gov.ae/en/",
        ]

        for url in urls_to_try:
            try:
                result = self.extract_visa_page(
                    url=url,
                    instructions=instructions,
                    schema=schema,
                    use_cache=False  # always fresh for nationality queries
                )
                # Cache by nationality key for this session
                self._set_cached(cache_key, result)
                return result
            except ContextDevError as e:
                print(f"  [NATIONALITY] Failed on {url}: {e} — trying next URL")
                continue

        # If all URLs fail, return a helpful fallback
        return {
            "data": {
                "nationality": nationality,
                "visa_requirement": f"Please check the official UAE government portal at u.ae or contact the nearest UAE embassy for the most up-to-date visa requirements for {nationality} passport holders.",
                "how_to_apply": "Visit https://u.ae/en/information-and-services/visa-and-emirates-id for official information."
            }
        }

    # ─────────────────────────────────────────────────────────────
    # DEDICATED TOPIC EXTRACTORS
    # ─────────────────────────────────────────────────────────────

    def get_emirates_id_info(self) -> dict:
        """
        Extracts Emirates ID application process, renewal, fees, required documents,
        and validity from official UAE government sources.
        """
        schema = {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "what_is_emirates_id": {"type": "string"},
                "who_needs_it": {"type": "string"},
                "required_documents": {"type": "array", "items": {"type": "string"}},
                "application_steps": {"type": "array", "items": {"type": "string"}},
                "validity": {"type": "string"},
                "fees_aed": {"type": "string"},
                "renewal_process": {"type": "string"},
                "where_to_apply": {"type": "string"}
            },
            "required": ["topic"]
        }
        return self.extract_visa_page(
            url=UAE_OFFICIAL_SOURCES["emirates_id"],
            instructions=(
                "Extract everything about the Emirates ID: what it is, who needs it (citizens, residents, GCC nationals), "
                "required documents, how to apply, fees in AED, validity period, renewal process, and where to apply "
                "(ICP service centres, typing centres, online portal). Be thorough and precise."
            ),
            schema=schema,
        )

    def get_overstay_fines_info(self) -> dict:
        """
        Extracts UAE overstay fines, grace period, and how to regularize visa status.
        """
        schema = {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "grace_period": {"type": "string"},
                "daily_fine_aed": {"type": "string"},
                "how_to_pay": {"type": "array", "items": {"type": "string"}},
                "how_to_regularize": {"type": "array", "items": {"type": "string"}},
                "consequences": {"type": "string"},
                "amnesty_info": {"type": "string"}
            },
            "required": ["topic"]
        }
        return self.extract_visa_page(
            url=UAE_OFFICIAL_SOURCES["overstay"],
            instructions=(
                "Extract the official UAE policy on overstaying a visa: the grace period after visa expiry, "
                "the daily fine amount in AED, how and where to pay fines (ICP, GDRFA), how to regularize "
                "your status (exit the country, apply for extension), and any consequences such as bans. "
                "If there is any amnesty programme mentioned, include it."
            ),
            schema=schema,
        )

    def get_family_sponsorship_info(self) -> dict:
        """
        Extracts family sponsorship visa rules: who can sponsor, documents, salary threshold, fees.
        """
        schema = {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "who_can_sponsor": {"type": "string"},
                "minimum_salary_aed": {"type": "string"},
                "eligible_family_members": {"type": "array", "items": {"type": "string"}},
                "required_documents": {"type": "array", "items": {"type": "string"}},
                "application_steps": {"type": "array", "items": {"type": "string"}},
                "validity": {"type": "string"},
                "fees_aed": {"type": "string"}
            },
            "required": ["topic"]
        }
        return self.extract_visa_page(
            url=UAE_OFFICIAL_SOURCES["family_sponsorship"],
            instructions=(
                "Extract the rules for sponsoring family members for UAE residency: who is eligible to sponsor "
                "(e.g. UAE residents, citizens), minimum monthly salary requirement in AED, which family members "
                "can be sponsored (spouse, children, parents), required documents, application steps via ICP or GDRFA, "
                "visa validity period, and fees in AED."
            ),
            schema=schema,
        )

    def get_green_visa_info(self) -> dict:
        """
        Extracts UAE Green Visa details: eligibility, categories, fees, validity.
        """
        schema = {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "what_is_green_visa": {"type": "string"},
                "eligibility_categories": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "requirements": {"type": "string"}
                        }
                    }
                },
                "key_benefits": {"type": "array", "items": {"type": "string"}},
                "validity": {"type": "string"},
                "how_to_apply": {"type": "string"}
            },
            "required": ["topic"]
        }
        return self.extract_visa_page(
            url=UAE_OFFICIAL_SOURCES["green_visa"],
            instructions=(
                "Extract the UAE Green Visa details: what it is, who qualifies (freelancers, skilled workers, "
                "investors, outstanding students), key benefits compared to regular residency (no sponsor needed, "
                "self-sponsorship, 5-year validity), how to apply, and any salary or qualification thresholds."
            ),
            schema=schema,
        )

    def get_retirement_visa_info(self) -> dict:
        """
        Extracts UAE retirement visa eligibility, financial requirements, and validity.
        """
        schema = {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "minimum_age": {"type": "string"},
                "financial_requirements": {"type": "array", "items": {"type": "string"}},
                "required_documents": {"type": "array", "items": {"type": "string"}},
                "validity": {"type": "string"},
                "how_to_apply": {"type": "string"}
            },
            "required": ["topic"]
        }
        return self.extract_visa_page(
            url=UAE_OFFICIAL_SOURCES["retirement_visa"],
            instructions=(
                "Extract UAE retirement visa details: minimum age requirement (55 years), financial thresholds "
                "(property value, savings amount, or monthly income in AED), required documents, "
                "visa validity period (5 years renewable), and how to apply via ICP or GDRFA."
            ),
            schema=schema,
        )
