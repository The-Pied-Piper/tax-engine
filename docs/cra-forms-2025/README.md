# CRA 2025 e-text forms (raw)

Downloaded unmodified with curl from `https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/<code>/<code>-25e.txt`
on Umar's machine on 2026-10-19 (cloud containers cannot reach canada.ca), then copied here.
sha256 checked against the download. Files are UTF-8 with BOM and CRLF line ends.

| File | Form |
|---|---|
| 5000-d1-25e.txt | Federal Worksheet |
| 5000-s2-25e.txt | Schedule 2 |
| 5000-s3-25e.txt | Schedule 3, Capital Gains or Losses |
| 5000-s5-25e.txt | Schedule 5, Amounts for Spouse and Dependants |
| t776-25e.txt | T776, Statement of Real Estate Rentals |
| 5006-r-25e.txt | T1 return, Ontario edition |
| 5006-c-25e.txt | Form ON428, Ontario Tax |
| 5006-a-25e.txt | Schedule ON428-A, LIFT credit |
| 5006-d-25e.txt | Worksheet ON428 |
| 5006-tc-25e.txt | Form ON479, Ontario Credits |
| 5006-tca-25e.txt | Schedule ON479-A, CARE credit |
| 5006-d1-25e.txt | Worksheet ON479 |
| 5006-tg-25e.txt | ON-BEN |
| 5006-s11-25e.txt | Schedule ON(S11) |
| 5000-g-25e.txt | General Income Tax and Benefit Guide 2025 (from `/formspubs/pub/5000-g/`, not `/pbg/`; the `/pbg/` URL 404s). sha256 d1da5d3d…68d8b7b1 |

No 2025 .txt exists for Schedule 1 (archived), T2209, T2091(IND), T2125 or T1A (PDF only), nor for
guides T4036 Rental Income and T4037 Capital Gains (HTML and PDF online; e-text only by mail order).
The General Guide's line 25300 section has no conversion chart; it says the claim depends on the
inclusion rates and refers to T4037.

## PDFs (no .txt published)
Downloaded unmodified with curl on Umar's machine on 2026-10-19, then copied here; sha256 checked
against the download. Forms are under `/formspubs/pbg/<code>/`, guides under `/formspubs/pub/<code>/`.
Umar accepted PDF quotes where CRA publishes no .txt (2026-10-19). Quotes on tickets were checked
against `pdftotext` output (plain and `-layout`).

| File | Form | sha256 |
|---|---|---|
| t2209-25e.pdf | T2209, Federal Foreign Tax Credits | 2a0f1cd37fdec2885e7231f3dff4976508825ea1b867dbfe8300933356abf539 |
| t2091ind-25e.pdf | T2091(IND), Principal Residence designation | 86199bfccd4a6c70e6522165b78d0cece30dbff21655e990a814c0d1c03e83e7 |
| t2125-25e.pdf | T2125, Business or Professional Activities | fae75091753cb1810404c00aaa3f2c1a91cfae942b73bace7e6b884f24a08738 |
| t1a-25e.pdf | T1A, Request for Loss Carryback | cfe11515c55863047eca93ba464523c5808592aa2d885a02323ce0aaf75c6059 |
| t4036-25e.pdf | Guide T4036, Rental Income | f34bf23a4b97e3fd11f1eb21d27bd5aeff3f1aefac3aa22128c9dd136e6f408c |
| t4037-25e.pdf | Guide T4037, Capital Gains | 8687687cabce3f26945c8f66581cb1167e1e149eb257d1ae1bb6d0958996139c |

| t1436-25e.pdf | T1436, Capital Gains Worksheet (line 25300 Chart A) | 3aec70975894e81e41f313219d8770a905ee0421992b36c175f529fc9265d07a |
| t4002-25e.pdf | Guide T4002, Self-employed Business Income (CCA rates; `/pub/`) | 8efc96434bfaab1beabe95b48d8cb3c764a6b2292e9865cb9aaeac938673453f |
| t2091ind-ws-23e.pdf | T2091(IND)-WS, Principal Residence Worksheet, **2023 edition** (CRA's current one; no 2024 or 2025 PDF) | bc9832b119d031595f5b34c86aad0afcf3be03340f36bc3bea9484a54757f649 |
| t2203-25e.pdf | T2203, Provincial and Territorial Taxes for Multiple Jurisdictions | a78d849d0dfe286e7b9750acf8bfccc494c9e59ae3e1d9415c64e379c8d7c48d |

The last four were downloaded 2026-10-19 on Umar's machine through headless Chrome (canada.ca drops
curl there too); none has a .txt (every .txt URL 404s).

## Third batch (2026-10-19)
Downloaded on Umar's machine through headless Chrome from `/formspubs/pbg/<code>/<code>-25e.(txt|pdf)`,
then copied here; sha256 checked against the download. The .txt files start with a UTF-8 BOM. The four
PDFs are here because their .txt URL 404s.

| File | Form | sha256 |
|---|---|---|
| 5006-s2-25e.txt | Schedule ON(S2), Provincial Amounts Transferred from your Spouse or Common-Law Partner | 6e68314aba25b10c337cde973e32f3c42191e6f8875d1278b0c6b87ea7ea605d |
| 5000-s8-25e.txt | Schedule 8, Canada Pension Plan Contributions and Overpayment | db859d06606fd7a13c7c2875ab5299d4780d37d8a28ffe77b9f0650d0ef988d2 |
| 5000-s9-25e.txt | Schedule 9, Donations and Gifts | 86988baa6d4a6918d202ec7beb167e57c9ae42136bbf2ca19125aada2b26cb06 |
| 5000-s11-25e.txt | Schedule 11, Federal Tuition Amount and Canada Training Credit | 8e9fae56e6168830d44ff97690a77c11bc0afb5ffcb65528e2a44b0eb2115393 |
| 5000-s13-25e.txt | Schedule 13, EI Premiums on Self-Employment and Other Eligible Earnings | f172ddfc8011e1ad59e171e427edf30320bf4ef9ae2e9486dbd1770476e6901c |
| t691-25e.pdf | T691, Alternative Minimum Tax (PDF only) | 7949e42864bd0d428b24af56bf3b4e23d7d1b277cf945abed1e099add1ddb7ea |
| t1206-25e.pdf | T1206, Tax on Split Income (PDF only) | 896a42d5be2fb7f36dd2d14a3744c60c1488ca12dffda9d219dfbbf9b9498061 |
| t2036-25e.pdf | T2036, Provincial or Territorial Foreign Tax Credit (PDF only) | 9eafaa97b1bb012fc75944affa32ef9345961b4ac73426cf3c1b8571f10c3770 |
| t1221-25e.pdf | T1221, Ontario Focused Flow-Through Share Resource Expenses (Individuals) (PDF only) | 73eb8d8558d604e199f6de042f4eac458c300e181f59a8bba24f7b121b538789 |

## Fourth batch (2026-10-19)
Downloaded on Umar's machine through headless Chrome from `/formspubs/pbg/<code>/<code>-25e.(txt|pdf)`;
sha256 checked against the download. Only Schedules 12 and 15 and T2222 publish a .txt; the rest are
PDF only (their .txt URL 404s), so quotes from them carry "(confirmed DATE from the PDF; no .txt
published)".

| File | Form | sha256 |
|---|---|---|
| t2042-25e.pdf | T2042, Statement of Farming Activities (PDF only) | 0223f8a766b06beb93a6e94282ffcd84c2265444b2992c35efc34185233b2597 |
| t2121-25e.pdf | T2121, Statement of Fishing Activities (PDF only) | 6667327bdd83502f826ac247e62fbc32e054b909160f1a540780a7773033381b |
| 5000-s15-25e.txt | Schedule 15, FHSA Contributions, Transfers and Activities | 6031f31255b0d406a41f59b92d99b95eb039ea11c5ca2683742d8d7d3ecd1f8f |
| t929-24e.pdf | T929, Disability Supports Deduction, **2024 edition** (no 2025 edition; PDF only) | 89b8dd2eff41f7887e0a880f7415cf079519a7313a8032bf2f074a187466f9a5 |
| t1-m-25e.pdf | T1-M, Moving Expenses Deduction (PDF only) | d33ce87b0ea135a4145aae7df824f6e5745f7bd03b6193b2958131a170d6a2fd |
| t1223-25e.pdf | T1223, Clergy Residence Deduction (PDF only) | ae7177e65c4dabaab6a05affde0aa0768d3872cafb670f6e32c1afd41c73a6c1 |
| t777-25e.pdf | T777, Statement of Employment Expenses (PDF only) | 99e767b0c8a2a841f66f516e28b5f9fe631d6dbd4db6eaae36cb7c82b93f1204 |
| t2048-25e.pdf | T2048, Capital Gains Deduction for Qualifying Business Transfers or Qualifying Cooperative Conversions (PDF only) | 75f4790ffb5e8b1dfcda6af0a68bff4fbe7852f149fbdcb5660b2c1f6ecc3734 |
| t657-25e.pdf | T657, Calculation of Capital Gains Deduction (PDF only) | 5ad7c7a95a4bcf24ecb909db8f1e24ed3f8707c4fab4c7987e149850f900d240 |
| t2222-25e.txt | T2222, Northern Residents Deductions | aedc9f64a7f8857415c9a8d18a20e0dc860601a88510a4b9710158816245ff53 |
| rc381-25e.pdf | RC381, Inter-Provincial Calculation for CPP and QPP Contributions and Overpayments (PDF only) | 3c472af23df02adc22f976d34cfca733e0d702e094f4f5f0335248d41c50fa9b |
| t2038-ind-25e.pdf | T2038(IND), Investment Tax Credit (Individuals) (PDF only; CRA's path is `t2038-ind`) | 782d8ade84f7b79f4f73624a992ea3668ee008b168d3ad0579ffd3d01db8b48d |
| t1172-25e.pdf | T1172, Additional Tax on Accumulated Income Payments from RESPs (PDF only) | 0985388e35ca1b70d6a92d0764d36b39b9754d9c8403cbb75426805ec4b052ef |
| rc359-25e.pdf | RC359, Tax on Excess Employees Profit Sharing Plan Amounts (PDF only) | 9561b6c3fb12904a01741515f32977cf23225de2e980d7091dc89bb275cb3ed5 |
| 5000-s12-25e.txt | Schedule 12, Multigenerational Home Renovation Tax Credit | 05a0a91988a533eb82f9222eb4133418dafdcdce51091b4e4dbdade376544b75 |
| t2043-25e.pdf | T2043, Return of Fuel Charge Proceeds to Farmers Tax Credit (PDF only) | 6f445e20f97ce7b7ba4204480b98342ee922a976069e3575464b5146f7f70e36 |
| t2204-25e.pdf | T2204, Employee Overpayment of Employment Insurance Premiums (PDF only) | 5b34eff9998812738dc116272db8cd20add88b84a3fde7532f580cd1fd11f987 |

Not saved, because CRA publishes no 2024 or 2025 file:
- **T1229**, Statement of Resource Expenses and Depletion Allowance: CRA's page links only
  `t1229-23e.pdf`; the 2024 and 2025 .txt and .pdf URLs 404.
- **T777S**, Statement of Employment Expenses for Working at Home Due to COVID-19: archived by CRA;
  the latest edition is 2022.
- **Line 25000 calculation chart** (other payments deduction over $93,454): an HTML table only, at
  https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-25000-other-payments-deduction.html.
  The first part of the calculation is in the Federal Worksheet, `5000-d1-25e.txt`.

## Fifth batch (2026-10-24)
Downloaded with curl from `https://www.canada.ca/content/dam/cra-arc/formspubs/<pbg|pub>/<code>/<code>-25e.(txt|pdf)`
(curl worked from Umar's machine today); sha256 computed on the saved file. The .txt files start with a UTF-8 BOM.
Forms are under `/pbg/`, guides under `/pub/`. GST370 has no .txt (404), so quotes from it carry
"(confirmed DATE from the PDF; no .txt published)".

| File | Form | sha256 |
|---|---|---|
| 5000-s6-25e.txt | Schedule 6, Canada Workers Benefit | eea18e6c3593e7289c1eb5f1279597bc6980203f01aeea5711cc9cdd1c07a7e1 |
| 5000-s7-25e.txt | Schedule 7, RRSP, PRPP and SPP Contributions and Transfers | 864d3de548746bdf7549d1b815a3387fd90334b372c6ba268d8733682d65cf22 |
| t778-25e.txt | T778, Child Care Expenses Deduction | 8424c9e03e8ab4e9d8e60addaec1140d0b9eba1480dffe4f68a8ddda0b21845d |
| gst370-25e.pdf | GST370, Employee and Partner GST/HST Rebate Application (PDF only) | e21d2363eb53be14414a1b5a08f04be402de79b1435c2a1eeef5aabbe2515113 |
| t4044-25e.txt | Guide T4044, Employment Expenses (from `/pub/t4044/`; the `/pbg/` path 404s) | 34102a0c7bc7856afed64ace707fd3c55e71d3b6a76af9e694011f9c80110587 |
| rc4064-25e.txt | Guide RC4064, Disability-Related Information (from `/pub/rc4064/`) | 178480bf91d5f45d8320444c28b3f011b436e1dbce57b8e8f060a5d169ba2e82 |

Not saved, because CRA publishes nothing new:
- **Ontario variant of Schedule 6**: none exists (`5006-s6-25e.txt` 404s); Ontario has no provincial
  Canada workers benefit schedule.
- **T691 guide or instructions**: CRA publishes only the form; the instructions are on the form itself.
  The PDF fetched today (`/pbg/t691/t691-25e.pdf`) has the same sha256 as the `t691-25e.pdf` already
  here; the `/pub/t691`, `/pbg/t691` .txt and `t691-instr` URLs 404.

## Web-page evidence (`web/`), 2026-10-24
These come from canada.ca HTML pages, not from CRA forms or guide files. Each is the page's main
content converted to plain text (scripts and navigation removed; tables as `|`-separated rows), fetched
on 2026-10-24. Per the process, a figure that only a web page states stays a listed check on its
ticket, not a confirmed form quote.

| File | Source page | sha256 |
|---|---|---|
| web/gst-hst-rates-by-province.txt | https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/gst-hst-businesses/charge-collect-which-rate.html (the rate tables are built by script; text taken from the page as rendered in headless Chrome). Current GST/HST and PST by province, and GST/HST since April 1, 2013 (for ticket #480) | d02e2265e4c4a95b05be29e784d82695d8816d5f7a9273ad3fb6f012c1597b69 |
| web/t4037-capital-gains-guide-web.txt | https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/t4037/capital-gains.html (HTML guide, including the capital gains deduction chapters) | c244e47eaec43455f3d684678d38288f2dd9f96c8c2929a1b857405fca505302 |
| web/line-12700-completing-schedule-3.txt | https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-12700-capital-gains/completing-schedule-3.html | 0048d932c56fd592281664a3b0f66fb5abea97459563cecbe4b93c02a9ae6144 |
| web/line-12700-calculating-reporting-capital-gains-losses.txt | same folder, `calculating-reporting-your-capital-gains-losses.html` | 1df94c69e6039320116f5d1bc456bc8c76b04b09b88c64811e7973b3a5f40793 |

## Fourth batch (2026-10-26)
Downloaded with curl on Umar's machine from `/formspubs/pbg/<code>/<code>-25e.(txt|pdf)`, then copied here;
sha256 checked against the download. T1032 has a .txt (starts with UTF-8 BOM); the other three have none (.txt URL 404s), so the PDF is kept.
Each PDF opened with `pdftotext` and is the 2025 edition.

| File | Form | sha256 |
|---|---|---|
| t1032-25e.txt | T1032, Joint Election to Split Pension Income | 78573350f788621d054608a092b5ff04a22f2641c62cb549363698061dca2b30 |
| t2017-25e.pdf | T2017, Summary of Reserves on Dispositions of Capital Property | 5e38f6e936549d7c2fb323a15b363f03f588e273bdd4ad29d2c530b986e61eb7 |
| t936-25e.pdf | T936, Calculation of Cumulative Net Investment Loss (CNIL) to December 31, 2025 | 26eb2f5989b4284d65c7c38d9e47a8ae30299275ea0a235b3c1267a343f163dd |
| t90-25e.pdf | T90, Income Exempt from Tax under the Indian Act | f85f6cf781da436dcb646b84d6ecbf1c84e51c96a83d5885722960c5c1c1eca4 |

## Fifth batch (2026-10-27)
Fetched on Umar's machine by a Remote Control session from `/formspubs/pbg/<code>/<code>-25e.pdf`, then copied here;
sha256 checked against the download (SHA256SUMS beside the originals). None has a .txt (the .txt URL 404s), so the PDF
is kept; quotes from them carry "(confirmed 2026-10-27 from the PDF; no .txt published)". T1229 has no 2025 edition.

| File | Form | sha256 |
|---|---|---|
| t1139-25e.pdf | T1139, Reconciliation of 2025 Business Income for Tax Purposes (PDF only) | 02e40097aff0bd33e1f78d2ad60daf911dbdda04d580a48bf38ced19abf83733 |
| t2205-25e.pdf | T2205, Amounts from a Spousal or Common-law Partner RRSP, RRIF, or SPP to Include in Income (PDF only) | 1636613273d155e09740d90a6e3e0db889346ba76a555f5964f7a564b5148f46 |
| t746-25e.pdf | T746, Calculating Your Deduction for Refund of Unused RRSP, PRPP, and SPP Contributions (PDF only) | 2447014b610884e7646a11be70fea56b5899a52e1f211aa3062f2c93445cbfe5 |
| t1043-25e.pdf | T1043, Deduction for Excess Registered Pension Plan Transfers You Withdrew from an RRSP, a PRPP, an SPP, or a RRIF (PDF only) | 8b53255d509ad9c146ab4bc3a67ab2fd32908e46d938cf0a26b3dea68471e4fe |
| t1212-25e.pdf | T1212, Statement of Deferred Security Options Benefits (PDF only) | 89a75392f31be3b16c719e6ce70c14be10f91de28e82ccaa69ae21b076654ff7 |

## Sixth batch (2026-10-27)
Saved with plain `curl -L -o` on Umar's machine (canada.ca blocks cloud containers), except IT-195R4, which Umar saved from his browser.
HTML pages are the raw page; the `.txt` beside each is the main content as text. sha256 of the files as saved.

| File | What | sha256 |
|---|---|---|
| t1032-25e.pdf | T1032, Joint Election to Split Pension Income, clean PDF from `/pbg/t1032/t1032-25e.pdf` (4 pages). The repo's `t1032-25e.txt` is garbled near line 21; use this PDF. | f94de1544cc73d44a533f64cea87cc5cc054d4b8ab3bd4e322012ff65c24b73b |
| t1032-25e.pdf.txt | `pdftotext -layout` extract of that PDF | 5bf57c482fc4cef65568aaac5d58c0e77898e131ea9fcc32a003b73c5e701a77 |
| t4068-25e.pdf | Guide T4068, Guide for the Partnership Information Return (T5013 Forms), 2025, from `/pub/t4068/t4068-25e.pdf` (106 pages; no .txt published) | 7b75f4f5f772754e490b56850b559b7721c1923ee4d5292aca66cddc09983456 |
| t4068-25e.pdf.txt | `pdftotext -layout` extract of that PDF | 465311e2fe9ccbbcf066c16c97df403b5fc22b32fbaca4dc5a4b6674a425114d |
| web/it195r4-rental-property-cca-restrictions.txt | ARCHIVED Interpretation Bulletin IT-195R4 (6 Sept 1991, page dated 2017-11-07), https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/it195r4.html, main content as text | d001c7255ffef1e2f4006102cde14ac05b2506acf9135fda88e4d161a21e6f38 |
| web/t1206-page.html (+ .txt) | T1206 form landing page (only the form PDFs; no Schedule 3 text) | ab5622302ea96bcc4042262bbac9383541b8c54a16acc9fa763d6d6cbe94fd58 |
| web/tosi-guidance-adults.html (+ .txt) | Guidance on the application of the split income rules for adults | 5cf9ed790567c6bb5350dea043883090c143a9d12429e9596e41f6b44e6f0c81 |
| web/tosi-excluded-shares.html (+ .txt) | Tax on split income - Excluded shares | 7bc837d13e962beae37ae7850a91a900a1e5111c88f3df2032178403109d515d |
| web/tosi-faq.html (+ .txt) | Frequently asked questions - Income sprinkling | 61712f9256f951d49ae0dfc45ce9e98de2b585212513f73bdc7c6eca99e9d515 |
| web/folio-s3-f4-c1.html (+ .txt) | Income Tax Folio S3-F4-C1, General Discussion of Capital Cost Allowance | be8685c4e3beca3fe50408753b6bd3d2a8c2ad232dde00a524db3e7efaa72454 |

The folios index lists no tax-on-split-income folio.
