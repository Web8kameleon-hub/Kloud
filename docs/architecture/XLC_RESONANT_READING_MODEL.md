# XLC Resonant Reading Model (MMM -> WWW)

## Qellimi
XLC ne kete projekt perdoret si menyre e re e leximit te pyetjeve dhe kthimit te shpejte te pergjigjeve, jo si primitive sigurie.

Modeli:
- MMM: momentum state nga input-i tekstual
- WWW: wave state qe reflekton output-in
- CC: coupling i dy gjendjeve (MMM x WWW)

Objektivi eshte qe input-i te kaloje mbi rreshtat e tekstit, te krijoje rezonance, dhe kjo rezonance te perdoret per vendim te shpejte te pergjigjes.

## Cfare eshte implementuar
- `LayerBuilder` nderton 3 shtresa per cdo sekuence:
  - WW (12D)
  - MM (12D)
  - CC (12D)
- Cdo shtrese normalizohet ne unit vector.
- Nanoide maten me `perf_counter_ns` per cdo shtrese dhe per totalin.
- `XLCInspector.inspect` ben krahasim direkt candidate vs reference.
- `XLCInspector.inspect_scan` ben scan mbi dritare te sekuences se pyetjes per te gjetur rezonancen me te forte (keyword-in brenda fjalise).

## Rrjedha e rekomanduar per pyetje direkte
1. Merr pyetjen input (tekst i lire).
2. Pastro ne sekuence simbolesh te njohura.
3. Përdor `inspect_scan` kundrejt references ose command-map.
4. Zgjidh kandidatin me `combined` me te larte.
5. Dergo te response-writer per gjenerim te shpejte te pergjigjes.

## Pse scan mode
Ne pyetje reale, fjala e targetit mund te jete brenda nje fjalie me shume zhurme.
Shembull:
- Input: `A je CLX?`
- Reference: `CLX`
- `inspect` i thjeshte krahason `AJECLX` me `CLX` (me pak i qendrueshem)
- `inspect_scan` gjen dritaren `CLX` dhe jep rezonancen reale te keyword-it.

## Semantika e scores
- `sim_ww`: ngjashmeria e vales
- `sim_mm`: ngjashmeria e momentumit
- `sim_cc`: ngjashmeria e coupling-ut
- `combined`: mesatarja e tre shtresave
- `resonance_score`: alias i `combined`

## NO_FAKE_DATA
- Cdo similarity llogaritet nga dot product real.
- Nuk ka fallback me score te shpikur.
- Nese nuk ka simbol te njohur, ngrihet gabim i vertete.

## Hapat e ardhshem
- `XLCCommandMap`: reference patterns per START/STOP/RESET/MODE
- `XLCResponseWriter`: map nga resonance-state ne output text
- `XLCBatchInspector`: scan paralel per throughput te larte
