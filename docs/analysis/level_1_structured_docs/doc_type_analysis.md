# Section start phrases per doc_type

Opening phrase of each labeled section in the PDFs in the `<doc_type>/` subfolders of this folder, in English and German.

## regulation (DORA 2022/2554, AI Act 2024/1689)

| Section | EN begins with | DE begins with |
| --- | --- | --- |
| `header` | `I` / `(Legislative acts)` (DORA), `REGULATION (EU) 2024/1689 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL` (AI Act) | `I` (DORA) |
| `citations` | `THE EUROPEAN PARLIAMENT AND THE COUNCIL OF THE EUROPEAN UNION,` | `DAS EUROPÄISCHE PARLAMENT UND DER RAT DER EUROPÄISCHEN UNION —` |
| `recitals` | `Whereas:` | `in Erwägung nachstehender Gründe:` |
| `enacting_formula` | `HAVE ADOPTED THIS REGULATION:` | `HABEN FOLGENDE VERORDNUNG ERLASSEN:` |
| `enacting_terms` | `CHAPTER I` | `KAPITEL I` |
| `final_formula` | `Done at Strasbourg, <date>.` (DORA), `Done at Brussels, <date>.` (AI Act) | `Geschehen zu Straßburg am <date>.` (DORA) |
| `annex` | `ANNEX I`, `ANNEX II`, … (AI Act only) | – |

The AI Act is only in English here (the German version is under `consolidated`), so the DE column covers DORA only.

## delegated_regulation (2016/98, 2024/1772, 2024/1773, 2024/1774, 2025/301, 2025/420, 2025/532)

| Section | EN begins with | DE begins with |
| --- | --- | --- |
| `header` | `COMMISSION DELEGATED REGULATION (EU) …` (2016/98: `REGULATIONS`) | `DELEGIERTE VERORDNUNG (EU) … DER KOMMISSION` |
| `citations` | `THE EUROPEAN COMMISSION,` | `DIE EUROPÄISCHE KOMMISSION —` |
| `recitals` | `Whereas:` | `in Erwägung nachstehender Gründe:` |
| `enacting_formula` | `HAS ADOPTED THIS REGULATION:` | `HAT FOLGENDE VERORDNUNG ERLASSEN:` |
| `enacting_terms` | `CHAPTER 1` (2016/98), `CHAPTER I` (2024/1772), `TITLE I` (2024/1774), `Article 1` (2024/1773, 2025/301, 2025/420, 2025/532) | `KAPITEL I` (2024/1772), `TITEL I` (2024/1774), `Artikel 1` (2024/1773, 2025/301, 2025/420, 2025/532) |
| `final_formula` | `Done at Brussels, <date>.` | `Brüssel, den <date>` |

None of the delegated regulations has an annex section. 2016/98 exists only in English.

## implementing_regulation (2024/2956, 2024/3172, 2025/302)

| Section | EN begins with | DE begins with |
| --- | --- | --- |
| `header` | `COMMISSION IMPLEMENTING REGULATION (EU) …` | `DURCHFÜHRUNGSVERORDNUNG (EU) … DER KOMMISSION` |
| `citations` | `THE EUROPEAN COMMISSION,` | `DIE EUROPÄISCHE KOMMISSION —` |
| `recitals` | `Whereas:` | `in Erwägung nachstehender Gründe:` |
| `enacting_formula` | `HAS ADOPTED THIS REGULATION:` | `HAT FOLGENDE VERORDNUNG ERLASSEN:` |
| `enacting_terms` | `Article 1` | `Artikel 1` |
| `final_formula` | `Done at Brussels, <date>.` | `Brüssel, den <date>` |
| `annex` | `ANNEX I`, `ANNEX II`, … | `ANHANG I`, `ANHANG II`, … |

In 2024/3172 the first annex section starts at `Section 1 – 'Disclosure of overview…'` (DE: `Abschnitt 1 – „Offenlegung…"`), not at `ANNEX I`. 2024/2956 exists only in English.

## consolidated

| Section | EN begins with | DE begins with |
| --- | --- | --- |
| `notice` | `This text is meant purely as a documentation tool and has no legal effect.` | `Dieser Text dient lediglich zu Informationszwecken und hat keine Rechtswirkung.` |
| `amendments` | `Amended by:` | `Geändert durch:` |
| `enacting_terms` | `TITLE I` (CRD, MiCA), `PART ONE` (CRR) | `TITEL I` (MiCA), `TEIL 1` (CRR), `KAPITEL I` (AI Act) |
| `annex` | `ANNEX I`, … | `ANHANG I`, … |

The consolidated AI Act (DE) has no `amendments` section.

## circular

### MaRisk (RS-05-2023-BA EN, RS-06-2024-BA DE)

| Section | EN begins with | DE begins with |
| --- | --- | --- |
| `header` | `Minimum Requirements for Risk Management` | `Rundschreiben` |
| `contents` | `Contents` | `Inhalt` |
| `general_part_AT` | `AT 1 Preliminary remarks` | `AT 1 Vorbemerkung` |
| `special_part_BT` | `BT 1 Special requirements relating to the internal control system` | `BT 1 Besondere Anforderungen an das interne …` |

### BAIT / VAIT (RS-10-2017-BA EN+DE, RS-10-2018-VA DE)

| Section | EN begins with | DE begins with |
| --- | --- | --- |
| `header` | `Circular 10/2017 (BA) in the version of …` | `Rundschreiben 10/2017 (BA) …` / `Rundschreiben 10/2018 (VA) …` |
| `contents` | `Contents` | `Inhalt` |
| `preliminary_remarks` | `I. Preliminary remarks` | `I. Vorbemerkung` |
| `requirements` | `II. Requirements` | `II. Anforderungen` |

## guideline (EBA/GL/2019/02)

| Section | EN begins with | DE begins with |
| --- | --- | --- |
| `header` | `Final Report on …` | `EBA/GL/2019/02` |
| `contents` | `Contents` | – |
| `executive_summary` | `Executive summary` | – |
| `background` | `Background` | – |
| `compliance_reporting` | `1. Compliance and reporting` | `1. Einhaltung und Meldepflichten` |
| `subject_scope_definitions` | `2. Subject matter, scope and definitions` | `2. Gegenstand, Anwendungsbereich …` |
| `implementation` | `3. Implementation` | `3. Umsetzung` |
| `guidelines` | `4. Guidelines on outsourcing` | `4. Leitlinien zu Auslagerungen` |
| `accompanying_documents` | `5. Accompanying documents` | – |

The DE guideline contains only the guidelines themselves, so sections marked "–" do not exist there.

## Notes

- Only one language is available for: 2016/98 (EN), 2024/2956 (EN), CRD (EN), AI Act (EN regulation, DE consolidated), VAIT (DE).
- Every page also has `footnotes` sections; they are left out here.
