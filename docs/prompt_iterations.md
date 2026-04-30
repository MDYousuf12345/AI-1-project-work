# Prompt Iterations

| Agent | Test Case | Score (/5) | Failure Type | Issue Found | Prompt Change | Result |
|------|----------|-----------|--------------|------------|--------------|--------|

| Lead Research | Delhi Public School Bangalore | 5 | None | Accurate output | No change | Good |
| Lead Research | Narayana School Hyderabad | 5 | None | Good pain points | No change | Good |
| Lead Research | St Xavier’s College | 4 | Generic output | Pain points too broad | Added: "Pain points must be specific and institution-relevant" | Improved |
| Lead Research | Small coaching centre | 3 | Missing detail | Output vague | Added: "If data is limited, infer realistic small-scale challenges" | Improved |
| Lead Research | New school no website | 3 | Missing fields | Many 'Not available' | Added: "Always provide best possible estimate instead of empty values" | Improved |
| Lead Research | Private school weak digital presence | 4 | Slightly generic | Lacked digital context | Added: "Include digital transformation issues if applicable" | Improved |
| Lead Research | School low admissions | 4 | Good | Minor improvement | No change | Good |
| Lead Research | Coaching institute | 3 | Generic | Pain points repeated | Added variation rule | Improved |

| Email | DPS Hyderabad | 5 | None | Good personalization | No change | Good |
| Email | Narayana School | 4 | Generic tone | Email slightly general | Added: "Use direct, personalized tone referencing institution" | Improved |
| Email | Small coaching centre | 3 | Weak personalization | Not specific | Added: "Mention institution type explicitly" | Improved |
| Email | Weak digital school | 4 | Good | Minor improvement | No change | Good |
| Email | Random institution | 2 | Off-topic | Email vague | Added: "Ensure email directly reflects pain points" | Fixed |
| Email | College case | 4 | Slightly long | Close to limit | Added strict word limit rule | Improved |
| Email | University case | 4 | Good | Minor tone issue | No change | Good |
| Email | New school | 3 | Generic | Missing urgency | Added urgency rule | Improved |

| Proposal | Hyderabad school | 5 | None | Complete proposal | No change | Good |
| Proposal | College system | 4 | Generic modules | Modules basic | Added: "Proposed modules must be detailed and specific" | Improved |
| Proposal | University case | 4 | Good | Minor improvement | No change | Good |
| Proposal | Small institute | 3 | Weak detail | Not structured well | Added: "Include structured business solution sections" | Improved |
| Proposal | No input case | 2 | Missing logic | Output vague | Added fallback logic rule | Fixed |
| Proposal | Multi-campus university | 4 | Good | Minor improvement | No change | Good |
| Proposal | Coaching centre | 3 | Generic | Lacked scale adaptation | Added scale-based solution rule | Improved |
| Proposal | Digital transformation case | 4 | Good | Minor improvement | No change | Good |