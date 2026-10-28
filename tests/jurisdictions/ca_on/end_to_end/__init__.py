"""CA-ON 2025, end to end: CRA's worked example computed from the manifest through the service.

The service is the one the composition root builds (`build_tax_computation`): the real YAML sources
over the jurisdiction packages and the shared registries. Return A's amounts (employment income
110000 and a capital gain of 20000 to total income 120000, the other Step 2 lines being 0 (the
Federal Worksheet's line 9, the eight sources of line 12100 added, less line 10, the part reported
in previous years, as line 11 and so the interest and other investment income, line 12100; lines
14400, 14500 and 14600 added to line 14700; and every income line, in line order, summed to line
15000); the CPP contributions computed from
employment income by Schedule 8's tiers, each at its maximum: base 3356.10, first additional 678.00
and second additional 396.00, the enhanced contributions 1074.00; the EI premiums computed from
employment income, at the maximum 1077.48; the RRSP contributions available to deduct of 1926, no
unused contributions plus the contributions of 1926 (Schedule 7 line 10), the most that may be
deducted, 1926, the lesser of them and the deduction limit of 19800 (Schedule 7 line 17), the amount
deducted of 1926 (line 18), at most that, as the RRSP deduction (line 20), and the unused
contributions carried forward of 0 (line 23), the contributions available less the deduction; less
that RRSP deduction, union dues of 2000, the child care expenses deduction of 0 (T1 line 21400, Form
T778 line 7, the least of the basic limit of line 4, 0 x 8000 + 0 x 11000 + 0 x 5000
= 0, the 0 paid of line 5 and two-thirds of the earned income of line 6, the employment
income of 110000, 73333.33..., rounded half-up to the cent, 73333.33: 0) and the enhanced
contributions to net income 115000, less no deductions from net income to taxable income
115000, and from each basic personal
amount (16129 federal, the Federal Worksheet's taper on net income, here at or below
the 177882 threshold so not reduced; 12747 Ontario) plus each amount for an eligible
dependant (T1 line 30400, Schedule 5 line 5, the federal basic personal amount less the
dependant's net income of 0; ON428 line 58160, the 11905.00 base less it, at most 10823), claimed
for 0 eligible dependants and so 0, the base CPP contributions and the EI premiums, and federally
the amount for infirm children of 0 x 2687 (line 30500) and the Canada employment amount of 1471
(the lesser of employment income and 1471), through each total of credit amounts and the credit rate
applied once to it (T1 line 33800, ON428 line 58840) to each form's non-refundable tax credits
(ON428 line 61500, which adds to line 46 the donations and gifts credit of lines 47 to 49 (line
58969), 5.05% of Schedule 9 line 13 and 11.16% of its line 14; T1 line 35000, which adds the
donations and gifts credit of Schedule 9 (line 34900) and the top-up tax credit of the Federal
Worksheet (line 34990); all 0 for donations of 0)
to each tax after credits, the Ontario
surtax on the Ontario tax after credits (ON428 lines 66 to 68) to the Ontario tax with surtax of
line 69, less the Ontario dividend tax credit of 0 (line 70, from line 57 and Worksheet ON428's
line 61520: no dividends), not below zero, to the Ontario tax after the dividend credit (line 71,
which is line 73 as line 72 is not triggered), and with no dependent children and no dependants
the Ontario tax reduction amounts of 294.00 (lines 74 to 77), twice them less line 73, not below
zero, the Ontario tax reduction of 0 (line 80), to the Ontario tax after the reduction (line 81);
Schedule ON428-A's
LIFT credit, 5.05% of employment income, 5555, at most 875 (lines 5 and 14), less 5% of net income
over 32500, 4125 (line 19), not below zero, 0 (line 20, ON428 line 85), taken off the Ontario tax
after the reduction, not below zero (line 86), less the community food program donation tax credit
for farmers, 25% of the qualifying donations (line 87), here 0 for donations of 0, not below zero
(line 88); and the Ontario health premium on taxable income by the chart of line 89, 750, added to
it to the Ontario tax of line 90; and on the T1, the federal tax after credits carried to the net
federal tax (line 42000), added to the Ontario tax (line 42800) to the total payable (line 43500);
Schedule 6's Canada workers benefit, computed for each family status, from the working income of
110000 (line 5, employment income), 27% of it over 3000 at most 1633 (line 22), less 15% of the
adjusted family net income (line 15, net income) of 115000 over 26855, 13221.75 (line 27), not below
zero, 0 (line 28), and with an eligible dependant 27% of the working income at most 2813, less 15%
of the adjusted family net income over 30639, 12654.15, not below zero, 0, the count of 0 Schedule 6
eligible dependants (line 38100) choosing the first (T1 line 45300); less the total credits (line
48200), here the chosen income tax deducted of 25000 (line 43700) plus that benefit, to the refund
or balance owing (line 167), 897.15, positive so a balance owing; every line computed from a dataset
rounded half-up to the cent) are checked from the files under `returns/` by
`test_worked_returns.py`, as are Returns B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, S, T, V, W
and X; the modules in this package pin which capability produces each line, the order, and the
trace that explains them.
"""
