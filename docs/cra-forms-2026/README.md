# CRA 2026 forms (raw)

Downloaded unmodified with curl on Umar's machine on 2026-11-07 from
`https://www.canada.ca/content/dam/cra-arc/formspubs/pub/<dir>/<file>` (the cloud cannot reach canada.ca;
curl works from this machine today). Link names were read from the CRA T4127 landing pages.
sha256 checked after download.

| File | What | sha256 |
|---|---|---|
| t4127-01-26e.pdf | T4127 Payroll Deductions Formulas, 122nd Edition, effective January 1, 2026 (`t4127-jan/`) | c715b8e6d33e0887119e0462b9a4cf8915370c56381932f1d7ba3a32385ddd8c |
| t4127-jul-26e.pdf | T4127, 123rd Edition, effective July 1, 2026 (`t4127-jul/`). Only reproduces changed sections; it says "no change for Ontario" and points to the 122nd for the rest | 69d86d952cb14c786fdcc0321ec293f66db1529276ef310217b3ade47db25671 |
| cc-on-01-26e.csv | Ontario claim codes, January | 7b14bb199aea89d7887690d569dd72e78be120421466dbe1eef13fa6a1418b74 |
| cc-fd-01-26e.csv | Federal claim codes, January | ed623d2b41f1879b08ef55ae0076c52d40ec51858026ad6f82ea978105ce373a |
| cpp-qpp-br-01-26e.csv | CPP/QPP base rate, January | 7d4f0f487f408590e2cbbb95ea65a5b5dd7052ae536da071a424ea147b3a5b87 |
| cpp-qpp-addntl-01-26e.csv | CPP/QPP additional contributions, January | 1362c4ca838bc9cab262eb6829904379adcd41fdd9ef5354496995d05aac9485 |
| cpp-qpp-scnd-addntl-01-26e.csv | CPP2 (second additional), January | aeeb9f2c042c11bb80ff744aa59edab56de43e523ef11109dd7985124a84448b |
| cpp-qpp-ttl-01-26e.csv | CPP/QPP total, January | a8254ad90584f10a92f11fe5d34c9c6c42c856b686a8bc26c632886387e9ece4 |
| ei-01-26e.csv | EI premium figures, January | 524162a6e1e62a7b2bdfe304a29f337273d03277519521a3cd380ec8e2fb0d1f |
| rtsncmtrshldcnstnt-01-26e.csv | Rates, income thresholds, constants, January | 3e708bcc916d37c6c4a0ccf37b651df615d5d7ca1651ad655e962013c369eb39 |
| thrrtsmnts-01-26e.csv | Other rates and amounts, January | 9f4d29d8a3ccf01c5c96b720e848ad779311e9fefdd50a10f6f514c4315f9b59 |
| rates-income-thresholds-constants-26e.csv | Rates, thresholds, constants, July | e3a690ccf861c14654279d89cdeca8ec018506edbfc950027518bf16bf728090 |
| other-rates-amounts-26e.csv | Other rates and amounts, July | d395b439d0e48846a05e5c578555d9a35e36aef58adbbf88b2eae2fcc2068bf8 |

## Not yet published (2026-11-07)
Every `-26e` URL below returned HTTP 404 (CRA's HTML 404 page). 2026 T1 forms normally appear in the
following January to February, so this is expected.

| Form | URL checked (under `https://www.canada.ca/content/dam/cra-arc/formspubs/`) |
|---|---|
| T1 General, Ontario (5006-r) | pbg/5006-r/5006-r-26e.txt and .pdf |
| ON428 (5006-c) | pbg/5006-c/5006-c-26e.txt and .pdf |
| ON428-A, LIFT (5006-a) | pbg/5006-a/5006-a-26e.txt and .pdf |
| Worksheet ON428 (5006-d) | pbg/5006-d/5006-d-26e.txt and .pdf |
| Federal Worksheet (5000-d1) | pbg/5000-d1/5000-d1-26e.txt and .pdf |
| Schedule 8, CPP/CPP2 (5000-s8) | pbg/5000-s8/5000-s8-26e.txt and .pdf |
| Schedule 6, CWB (5000-s6) | pbg/5000-s6/5000-s6-26e.txt and .pdf |
| Schedules 1, 2, 3, 5 | pbg/5000-s1,s2,s3,s5/5000-sN-26e.txt |
| T1 General Guide (5000-g) | pub/5000-g/5000-g-26e.txt and .pdf |
| T1-M | pbg/t1-m/t1-m-26e.pdf |
| T4032ON payroll tables | pub/t4032on-jan/t4032on-jan-26e.(pdf\|txt), pub/t4032on-jul/t4032on-jul-26e.pdf |

Control: the same URL pattern with `-25e` (e.g. 5006-r, 5000-s8, 5000-s6) returns 200, so the 404s are real.
