"""
Conflict Detection Module — identifies contradictions across document sources,
prioritizes by date, and explains reasoning.
"""
import re
from datetime import datetime


def detect_conflicts(retrieved_chunks):
    """
    Analyze retrieved chunks for potential conflicts.
    Groups chunks by source document, identifies overlapping claims,
    and flags contradictions.
    
    Returns:
        {
            "has_conflicts": bool,
            "conflicts": [
                {
                    "topic": str,
                    "sources": [
                        {
                            "source": str,
                            "source_type": str,
                            "value": str,
                            "date": str | None,
                            "location": str,
                            "text_excerpt": str,
                        }
                    ],
                    "resolution": {
                        "chosen_source": str,
                        "reason": str,
                        "confidence": float,
                    }
                }
            ],
            "trusted_sources": [str],  # ordered by priority
        }
    """
    if not retrieved_chunks:
        return {"has_conflicts": False, "conflicts": [], "trusted_sources": []}

    # Group chunks by source document
    by_source = {}
    for chunk in retrieved_chunks:
        meta = chunk.get("metadata", {})
        source = meta.get("source", "Unknown")
        if source not in by_source:
            by_source[source] = {
                "source": source,
                "source_type": meta.get("source_type", "unknown"),
                "chunks": [],
                "date": None,
            }
        by_source[source]["chunks"].append(chunk)

        # Try to extract date from metadata or text
        if by_source[source]["date"] is None:
            date = _extract_date_from_chunk(chunk)
            if date:
                by_source[source]["date"] = date

    # Build source priority list (newest first)
    sources_list = list(by_source.values())
    sources_with_dates = [s for s in sources_list if s["date"]]
    sources_without_dates = [s for s in sources_list if not s["date"]]

    sources_with_dates.sort(key=lambda s: s["date"], reverse=True)
    ordered_sources = sources_with_dates + sources_without_dates

    trusted_sources = [s["source"] for s in ordered_sources]

    # Extract numerical values and key claims for conflict comparison
    source_values = {}
    for src_info in sources_list:
        values = set()
        for chunk in src_info["chunks"]:
            text = chunk.get("text", "")
            # Extract percentages
            pcts = re.findall(r"(\d+(?:\.\d+)?)\s*%", text)
            for p in pcts:
                values.add(f"{p}%")
            # Extract dollar amounts
            dollars = re.findall(r"\$\s*([\d,]+(?:\.\d+)?)", text)
            for d in dollars:
                values.add(f"${d}")
        source_values[src_info["source"]] = values

    # Detect conflicts: different sources have different values
    conflicts = []
    source_names = list(source_values.keys())
    conflicting_pairs = set()

    for i in range(len(source_names)):
        for j in range(i + 1, len(source_names)):
            s1, s2 = source_names[i], source_names[j]
            v1, v2 = source_values[s1], source_values[s2]
            if v1 and v2 and v1 != v2:
                overlap_type = _determine_conflict_type(v1, v2)
                if overlap_type:
                    conflicting_pairs.add((s1, s2))

    if conflicting_pairs:
        # Build conflict report
        conflict_sources = []
        for src_info in ordered_sources:
            src_name = src_info["source"]
            vals = source_values.get(src_name, set())
            if vals:
                # Get excerpt from first chunk
                excerpt = src_info["chunks"][0]["text"][:200] if src_info["chunks"] else ""
                conflict_sources.append({
                    "source": src_name,
                    "source_type": src_info["source_type"],
                    "value": ", ".join(sorted(vals)),
                    "date": src_info["date"].strftime("%b %d, %Y") if src_info["date"] else None,
                    "location": src_info["chunks"][0].get("metadata", {}).get("location", ""),
                    "text_excerpt": excerpt,
                })

        # Resolution: trust the newest source
        chosen = ordered_sources[0] if ordered_sources else None
        chosen_name = chosen["source"] if chosen else "Unknown"
        chosen_date = chosen["date"].strftime("%b %d, %Y") if chosen and chosen["date"] else "Unknown date"

        conflicts.append({
            "topic": "Value discrepancy detected across sources",
            "sources": conflict_sources,
            "resolution": {
                "chosen_source": chosen_name,
                "reason": (
                    f"The system prioritized '{chosen_name}' (dated {chosen_date}) "
                    f"as the most recent document. Newer documents are given higher "
                    f"trust weight because they are more likely to reflect current "
                    f"policies, pricing, or decisions."
                ),
                "confidence": 0.85 if chosen and chosen["date"] else 0.60,
            },
        })

    return {
        "has_conflicts": len(conflicts) > 0,
        "conflicts": conflicts,
        "trusted_sources": trusted_sources,
    }


def _extract_date_from_chunk(chunk):
    """Extract a date from chunk metadata or text."""
    meta = chunk.get("metadata", {})

    # Try metadata fields first
    for field in ["date", "created", "modified", "upload_date"]:
        if field in meta and meta[field]:
            try:
                from dateutil import parser as dp
                return dp.parse(str(meta[field]))
            except (ValueError, TypeError):
                pass

    # Try extracting from text
    text = chunk.get("text", "")
    patterns = [
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{1,2}/\d{1,2}/\d{2,4})",
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s*\d{4})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                from dateutil import parser as dp
                return dp.parse(match.group(1), fuzzy=True)
            except (ValueError, TypeError):
                continue

    return None


def _determine_conflict_type(values1, values2):
    """
    Determine if two sets of extracted values actually conflict.
    Returns a description of the conflict type or None.
    """
    # Check for percentage conflicts
    pct1 = {v for v in values1 if v.endswith("%")}
    pct2 = {v for v in values2 if v.endswith("%")}
    if pct1 and pct2 and pct1 != pct2:
        return "percentage_conflict"

    # Check for dollar amount conflicts
    dol1 = {v for v in values1 if v.startswith("$")}
    dol2 = {v for v in values2 if v.startswith("$")}
    if dol1 and dol2 and dol1 != dol2:
        return "price_conflict"

    return None
