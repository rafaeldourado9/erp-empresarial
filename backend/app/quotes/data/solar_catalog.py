"""
Catálogo estático de módulos fotovoltaicos e inversores solares.
Dados pré-carregados — usuários nunca inserem itens manualmente.
Abrange as principais marcas do mercado mundial disponíveis no Brasil.
"""
from __future__ import annotations

from typing import TypedDict


# ---------------------------------------------------------------------------
# Módulos fotovoltaicos
# ---------------------------------------------------------------------------

class ModuloSolar(TypedDict):
    id: str
    marca: str
    modelo: str
    potencia_wp: int
    eficiencia: float          # % (ex: 21.3)
    tipo: str                  # monocristalino | policristalino | bifacial | half_cell | topcon | hjt
    largura_mm: int
    altura_mm: int
    espessura_mm: int
    peso_kg: float
    garantia_produto_anos: int
    garantia_potencia_anos: int
    potencia_min_25anos: float # % da potência nominal aos 25 anos
    corrente_isc: float        # A
    tensao_voc: float          # V
    url_datasheet: str


MODULOS: list[ModuloSolar] = [
    # ── LONGi Solar ──────────────────────────────────────────────────────────
    {"id":"longi-hi-mo5-415","marca":"LONGi","modelo":"Hi-MO5 LR4-60HIH-415M","potencia_wp":415,"eficiencia":21.3,"tipo":"half_cell","largura_mm":1008,"altura_mm":1978,"espessura_mm":35,"peso_kg":20.9,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.08,"tensao_voc":37.60,"url_datasheet":""},
    {"id":"longi-hi-mo6-550","marca":"LONGi","modelo":"Hi-MO6 LR5-72HIH-550M","potencia_wp":550,"eficiencia":21.3,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.5,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.05,"tensao_voc":49.35,"url_datasheet":""},
    {"id":"longi-hi-mo6-575","marca":"LONGi","modelo":"Hi-MO6 LR5-72HIH-575M","potencia_wp":575,"eficiencia":22.1,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.5,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.45,"tensao_voc":49.95,"url_datasheet":""},
    {"id":"longi-hi-mo-x6-585","marca":"LONGi","modelo":"Hi-MO X6 LR5-72HGH-585M","potencia_wp":585,"eficiencia":22.6,"tipo":"topcon","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":29.0,"garantia_produto_anos":15,"garantia_potencia_anos":30,"potencia_min_25anos":87.40,"corrente_isc":14.66,"tensao_voc":50.35,"url_datasheet":""},
    {"id":"longi-hi-mo-x6-600","marca":"LONGi","modelo":"Hi-MO X6 LR5-72HGH-600M","potencia_wp":600,"eficiencia":23.0,"tipo":"topcon","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":29.0,"garantia_produto_anos":15,"garantia_potencia_anos":30,"potencia_min_25anos":87.40,"corrente_isc":14.90,"tensao_voc":50.75,"url_datasheet":""},

    # ── JA Solar ─────────────────────────────────────────────────────────────
    {"id":"jasolar-jam60s20-385","marca":"JA Solar","modelo":"JAM60S20 385/MR","potencia_wp":385,"eficiencia":20.4,"tipo":"half_cell","largura_mm":1004,"altura_mm":1879,"espessura_mm":30,"peso_kg":19.5,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":11.84,"tensao_voc":41.35,"url_datasheet":""},
    {"id":"jasolar-jam72s30-545","marca":"JA Solar","modelo":"JAM72S30 545/MR","potencia_wp":545,"eficiencia":21.0,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.95,"tensao_voc":49.58,"url_datasheet":""},
    {"id":"jasolar-jam72d40-575","marca":"JA Solar","modelo":"JAM72D40 575/MB","potencia_wp":575,"eficiencia":22.1,"tipo":"bifacial","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.5,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.47,"tensao_voc":50.02,"url_datasheet":""},
    {"id":"jasolar-jam72d40-600","marca":"JA Solar","modelo":"JAM72D40 600/MB","potencia_wp":600,"eficiencia":23.0,"tipo":"bifacial","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":29.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.86,"tensao_voc":51.00,"url_datasheet":""},
    {"id":"jasolar-jam54d40-435","marca":"JA Solar","modelo":"JAM54D40 435/MB","potencia_wp":435,"eficiencia":22.4,"tipo":"bifacial","largura_mm":1048,"altura_mm":1855,"espessura_mm":30,"peso_kg":22.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.53,"tensao_voc":41.93,"url_datasheet":""},

    # ── Canadian Solar ────────────────────────────────────────────────────────
    {"id":"canadian-cs3w-425","marca":"Canadian Solar","modelo":"CS3W-425MS HiKu","potencia_wp":425,"eficiencia":20.6,"tipo":"monocristalino","largura_mm":1048,"altura_mm":1970,"espessura_mm":40,"peso_kg":22.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.17,"tensao_voc":41.47,"url_datasheet":""},
    {"id":"canadian-cs6w-555","marca":"Canadian Solar","modelo":"CS6W-555MS HiKu6","potencia_wp":555,"eficiencia":21.4,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.3,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.22,"tensao_voc":49.90,"url_datasheet":""},
    {"id":"canadian-cs6w-580","marca":"Canadian Solar","modelo":"CS6W-580MS HiKu6","potencia_wp":580,"eficiencia":22.3,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.3,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.62,"tensao_voc":50.35,"url_datasheet":""},
    {"id":"canadian-cs6r-430","marca":"Canadian Solar","modelo":"CS6R-430T TOPBiHiKu6","potencia_wp":430,"eficiencia":22.1,"tipo":"topcon","largura_mm":1048,"altura_mm":1855,"espessura_mm":35,"peso_kg":22.5,"garantia_produto_anos":15,"garantia_potencia_anos":30,"potencia_min_25anos":87.40,"corrente_isc":13.65,"tensao_voc":42.30,"url_datasheet":""},
    {"id":"canadian-cs3y-460","marca":"Canadian Solar","modelo":"CS3Y-460MS HiKu7","potencia_wp":460,"eficiencia":23.2,"tipo":"topcon","largura_mm":1134,"altura_mm":1762,"espessura_mm":35,"peso_kg":23.5,"garantia_produto_anos":15,"garantia_potencia_anos":30,"potencia_min_25anos":87.40,"corrente_isc":13.98,"tensao_voc":43.50,"url_datasheet":""},

    # ── Jinko Solar ───────────────────────────────────────────────────────────
    {"id":"jinko-tiger-pro-545","marca":"Jinko Solar","modelo":"JKM545M-72HL4-V Tiger Pro","potencia_wp":545,"eficiencia":21.0,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.97,"tensao_voc":49.52,"url_datasheet":""},
    {"id":"jinko-tiger-neo-570","marca":"Jinko Solar","modelo":"JKM570N-72HL4-V Tiger Neo","potencia_wp":570,"eficiencia":21.96,"tipo":"topcon","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.5,"garantia_produto_anos":15,"garantia_potencia_anos":30,"potencia_min_25anos":87.40,"corrente_isc":14.28,"tensao_voc":50.05,"url_datasheet":""},
    {"id":"jinko-tiger-neo-605","marca":"Jinko Solar","modelo":"JKM605N-78HL4-V Tiger Neo","potencia_wp":605,"eficiencia":22.53,"tipo":"topcon","largura_mm":1134,"altura_mm":2382,"espessura_mm":35,"peso_kg":30.0,"garantia_produto_anos":15,"garantia_potencia_anos":30,"potencia_min_25anos":87.40,"corrente_isc":14.73,"tensao_voc":50.85,"url_datasheet":""},
    {"id":"jinko-bifacial-560","marca":"Jinko Solar","modelo":"JKM560M-72HL4-BDVP Tiger Pro Bifacial","potencia_wp":560,"eficiencia":21.5,"tipo":"bifacial","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.3,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.07,"tensao_voc":49.70,"url_datasheet":""},

    # ── Trina Solar ───────────────────────────────────────────────────────────
    {"id":"trina-vertex-550","marca":"Trina Solar","modelo":"TSM-DE18M.08(II) Vertex 550W","potencia_wp":550,"eficiencia":21.1,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":27.9,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.96,"tensao_voc":49.58,"url_datasheet":""},
    {"id":"trina-vertex-s-420","marca":"Trina Solar","modelo":"TSM-DE09R.08 Vertex S 420W","potencia_wp":420,"eficiencia":21.5,"tipo":"half_cell","largura_mm":1004,"altura_mm":1754,"espessura_mm":30,"peso_kg":20.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.50,"tensao_voc":39.60,"url_datasheet":""},
    {"id":"trina-vertex-n-590","marca":"Trina Solar","modelo":"TSM-NEG18R.28 Vertex N 590W","potencia_wp":590,"eficiencia":22.7,"tipo":"topcon","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.5,"garantia_produto_anos":15,"garantia_potencia_anos":30,"potencia_min_25anos":87.40,"corrente_isc":14.62,"tensao_voc":50.70,"url_datasheet":""},
    {"id":"trina-vertex-n-610","marca":"Trina Solar","modelo":"TSM-NEG19R.20 Vertex N 610W","potencia_wp":610,"eficiencia":23.5,"tipo":"topcon","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.5,"garantia_produto_anos":15,"garantia_potencia_anos":30,"potencia_min_25anos":87.40,"corrente_isc":14.84,"tensao_voc":51.60,"url_datasheet":""},

    # ── BYD Solar ─────────────────────────────────────────────────────────────
    {"id":"byd-p6k-36-415","marca":"BYD","modelo":"BYD P6K36-415 Mono","potencia_wp":415,"eficiencia":20.6,"tipo":"monocristalino","largura_mm":1016,"altura_mm":1978,"espessura_mm":40,"peso_kg":21.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":12.82,"tensao_voc":41.84,"url_datasheet":""},
    {"id":"byd-p6k-36-550","marca":"BYD","modelo":"BYD P6K36H-550 Half-Cut","potencia_wp":550,"eficiencia":21.1,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.03,"tensao_voc":49.48,"url_datasheet":""},
    {"id":"byd-p6k-72h-575","marca":"BYD","modelo":"BYD P6K72H-575 Bifacial","potencia_wp":575,"eficiencia":22.1,"tipo":"bifacial","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.5,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.52,"tensao_voc":50.05,"url_datasheet":""},

    # ── Risen Energy ──────────────────────────────────────────────────────────
    {"id":"risen-rsp-400","marca":"Risen Energy","modelo":"RSP400-6MH-F Mono PERC","potencia_wp":400,"eficiencia":20.6,"tipo":"monocristalino","largura_mm":1000,"altura_mm":1960,"espessura_mm":35,"peso_kg":20.5,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":12.54,"tensao_voc":41.31,"url_datasheet":""},
    {"id":"risen-rsm40-8-405","marca":"Risen Energy","modelo":"RSM40-8-405M Half-Cut","potencia_wp":405,"eficiencia":20.8,"tipo":"half_cell","largura_mm":1003,"altura_mm":1979,"espessura_mm":30,"peso_kg":20.2,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":12.69,"tensao_voc":40.68,"url_datasheet":""},
    {"id":"risen-rsm132-8-660","marca":"Risen Energy","modelo":"RSM132-8-660N TopBidium","potencia_wp":660,"eficiencia":22.5,"tipo":"topcon","largura_mm":1303,"altura_mm":2384,"espessura_mm":35,"peso_kg":38.0,"garantia_produto_anos":15,"garantia_potencia_anos":30,"potencia_min_25anos":87.40,"corrente_isc":18.50,"tensao_voc":52.00,"url_datasheet":""},

    # ── Suntech ───────────────────────────────────────────────────────────────
    {"id":"suntech-stc380-50","marca":"Suntech","modelo":"STP380S-B60/Wnh Mono PERC","potencia_wp":380,"eficiencia":19.6,"tipo":"monocristalino","largura_mm":998,"altura_mm":1956,"espessura_mm":40,"peso_kg":20.8,"garantia_produto_anos":10,"garantia_potencia_anos":25,"potencia_min_25anos":80.70,"corrente_isc":11.54,"tensao_voc":40.50,"url_datasheet":""},
    {"id":"suntech-stc550-24","marca":"Suntech","modelo":"STP550S-C54/Wnh HiDi HC","potencia_wp":550,"eficiencia":21.1,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.84,"tensao_voc":49.96,"url_datasheet":""},

    # ── Astronergy (CHINT Solar) ──────────────────────────────────────────────
    {"id":"astronergy-astro5s-420","marca":"Astronergy","modelo":"CHSM54M-HC 420W Astro5s","potencia_wp":420,"eficiencia":21.6,"tipo":"half_cell","largura_mm":1048,"altura_mm":1857,"espessura_mm":30,"peso_kg":21.2,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.66,"tensao_voc":39.96,"url_datasheet":""},
    {"id":"astronergy-astro6s-555","marca":"Astronergy","modelo":"CHSM72M-HC 555W Astro6s","potencia_wp":555,"eficiencia":21.3,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.1,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.06,"tensao_voc":50.12,"url_datasheet":""},
    {"id":"astronergy-topcon-580","marca":"Astronergy","modelo":"CHSM72N-HC 580W TOPCon","potencia_wp":580,"eficiencia":22.3,"tipo":"topcon","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.5,"garantia_produto_anos":15,"garantia_potencia_anos":30,"potencia_min_25anos":87.40,"corrente_isc":14.53,"tensao_voc":50.60,"url_datasheet":""},

    # ── Hanwha Q CELLS ────────────────────────────────────────────────────────
    {"id":"qcells-q-peak-415","marca":"Hanwha Q CELLS","modelo":"Q.PEAK DUO BLK ML-G10+ 415","potencia_wp":415,"eficiencia":21.4,"tipo":"half_cell","largura_mm":1016,"altura_mm":1766,"espessura_mm":32,"peso_kg":19.9,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":86.00,"corrente_isc":13.24,"tensao_voc":38.95,"url_datasheet":""},
    {"id":"qcells-q-tron-450","marca":"Hanwha Q CELLS","modelo":"Q.TRON BLK M-G2+ 450","potencia_wp":450,"eficiencia":22.3,"tipo":"hjt","largura_mm":1096,"altura_mm":1842,"espessura_mm":25,"peso_kg":22.5,"garantia_produto_anos":25,"garantia_potencia_anos":30,"potencia_min_25anos":92.00,"corrente_isc":13.76,"tensao_voc":43.40,"url_datasheet":""},

    # ── REC Group ────────────────────────────────────────────────────────────
    {"id":"rec-alpha-430","marca":"REC Group","modelo":"REC430AA Pure-R Alpha Series","potencia_wp":430,"eficiencia":22.3,"tipo":"hjt","largura_mm":1016,"altura_mm":1821,"espessura_mm":30,"peso_kg":21.0,"garantia_produto_anos":20,"garantia_potencia_anos":25,"potencia_min_25anos":92.00,"corrente_isc":13.87,"tensao_voc":41.70,"url_datasheet":""},
    {"id":"rec-twinpeak-410","marca":"REC Group","modelo":"REC410TP3 TwinPeak 3","potencia_wp":410,"eficiencia":21.1,"tipo":"half_cell","largura_mm":1016,"altura_mm":1916,"espessura_mm":40,"peso_kg":21.6,"garantia_produto_anos":20,"garantia_potencia_anos":25,"potencia_min_25anos":92.00,"corrente_isc":12.90,"tensao_voc":40.91,"url_datasheet":""},

    # ── Seraphim ─────────────────────────────────────────────────────────────
    {"id":"seraphim-srs-405","marca":"Seraphim","modelo":"SRS-405-6MBB Half-Cell","potencia_wp":405,"eficiencia":20.8,"tipo":"half_cell","largura_mm":1000,"altura_mm":1965,"espessura_mm":35,"peso_kg":20.5,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":12.68,"tensao_voc":40.98,"url_datasheet":""},
    {"id":"seraphim-srp-550","marca":"Seraphim","modelo":"SRP-550-BMA Bifacial","potencia_wp":550,"eficiencia":21.1,"tipo":"bifacial","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.1,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.06,"tensao_voc":49.59,"url_datasheet":""},

    # ── DAH Solar ─────────────────────────────────────────────────────────────
    {"id":"dah-dhm-54x10-415","marca":"DAH Solar","modelo":"DHM-54X10/FS(BW)-415W Half-Cell","potencia_wp":415,"eficiencia":21.3,"tipo":"half_cell","largura_mm":1008,"altura_mm":1972,"espessura_mm":35,"peso_kg":20.5,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.18,"tensao_voc":41.33,"url_datasheet":""},
    {"id":"dah-dhm-72x10-545","marca":"DAH Solar","modelo":"DHM-72X10/FS(BW)-545W Half-Cell","potencia_wp":545,"eficiencia":20.9,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.1,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.02,"tensao_voc":49.45,"url_datasheet":""},

    # ── OSDA ──────────────────────────────────────────────────────────────────
    {"id":"osda-os-410-m210","marca":"OSDA","modelo":"OS-410M 210mm Half-Cell","potencia_wp":410,"eficiencia":21.1,"tipo":"half_cell","largura_mm":1048,"altura_mm":1855,"espessura_mm":30,"peso_kg":20.8,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.31,"tensao_voc":40.14,"url_datasheet":""},
    {"id":"osda-os-550-bifacial","marca":"OSDA","modelo":"OS-550MB Bifacial Half-Cell","potencia_wp":550,"eficiencia":21.1,"tipo":"bifacial","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.00,"tensao_voc":49.56,"url_datasheet":""},

    # ── GCL Solar ─────────────────────────────────────────────────────────────
    {"id":"gcl-gm60-400","marca":"GCL Solar","modelo":"GCL-M6/72H-400 Half-Cell","potencia_wp":400,"eficiencia":20.6,"tipo":"half_cell","largura_mm":1000,"altura_mm":1960,"espessura_mm":35,"peso_kg":20.2,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":12.60,"tensao_voc":41.12,"url_datasheet":""},
    {"id":"gcl-gm10-550","marca":"GCL Solar","modelo":"GCL-M10/72H-550 Half-Cell","potencia_wp":550,"eficiencia":21.2,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.02,"tensao_voc":49.50,"url_datasheet":""},

    # ── SolarEdge ─────────────────────────────────────────────────────────────
    {"id":"solaredge-sep-400","marca":"SolarEdge","modelo":"SEP-400-B0F0D02 Pure R","potencia_wp":400,"eficiencia":20.6,"tipo":"monocristalino","largura_mm":1000,"altura_mm":1961,"espessura_mm":35,"peso_kg":20.5,"garantia_produto_anos":25,"garantia_potencia_anos":30,"potencia_min_25anos":86.00,"corrente_isc":12.62,"tensao_voc":40.92,"url_datasheet":""},

    # ── First Solar (CdTe thin-film) ──────────────────────────────────────────
    {"id":"firstsolar-fs6-455","marca":"First Solar","modelo":"FS-6455 Series 6 Plus","potencia_wp":455,"eficiencia":19.3,"tipo":"thin_film","largura_mm":1232,"altura_mm":2009,"espessura_mm":49,"peso_kg":32.0,"garantia_produto_anos":10,"garantia_potencia_anos":30,"potencia_min_25anos":90.10,"corrente_isc":3.97,"tensao_voc":219.90,"url_datasheet":""},

    # ── Panasonic EverVolt HIT ────────────────────────────────────────────────
    {"id":"panasonic-evervolt-380","marca":"Panasonic","modelo":"EVPV380H EverVolt HIT","potencia_wp":380,"eficiencia":21.7,"tipo":"hjt","largura_mm":1052,"altura_mm":1765,"espessura_mm":35,"peso_kg":19.0,"garantia_produto_anos":25,"garantia_potencia_anos":25,"potencia_min_25anos":92.00,"corrente_isc":12.30,"tensao_voc":43.90,"url_datasheet":""},
    {"id":"panasonic-evervolt-430","marca":"Panasonic","modelo":"EVPV430H EverVolt HIT+","potencia_wp":430,"eficiencia":22.2,"tipo":"hjt","largura_mm":1052,"altura_mm":1840,"espessura_mm":35,"peso_kg":20.2,"garantia_produto_anos":25,"garantia_potencia_anos":25,"potencia_min_25anos":92.00,"corrente_isc":13.24,"tensao_voc":44.50,"url_datasheet":""},

    # ── Silfab Solar ─────────────────────────────────────────────────────────
    {"id":"silfab-sla-400","marca":"Silfab Solar","modelo":"SLA 400 M Black Mono","potencia_wp":400,"eficiencia":20.6,"tipo":"monocristalino","largura_mm":1000,"altura_mm":1960,"espessura_mm":35,"peso_kg":20.5,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":85.00,"corrente_isc":12.62,"tensao_voc":40.76,"url_datasheet":""},

    # ── Waaree Energies ───────────────────────────────────────────────────────
    {"id":"waaree-ws-535","marca":"Waaree","modelo":"WS-535 Mono Percium","potencia_wp":535,"eficiencia":20.7,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":27.5,"garantia_produto_anos":10,"garantia_potencia_anos":25,"potencia_min_25anos":82.00,"corrente_isc":13.75,"tensao_voc":49.25,"url_datasheet":""},

    # ── Vikram Solar ──────────────────────────────────────────────────────────
    {"id":"vikram-somera-400","marca":"Vikram Solar","modelo":"VSMD108HD 400W Somera","potencia_wp":400,"eficiencia":20.6,"tipo":"half_cell","largura_mm":1000,"altura_mm":1960,"espessura_mm":35,"peso_kg":20.3,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":12.62,"tensao_voc":40.78,"url_datasheet":""},

    # ── Amerisolar ────────────────────────────────────────────────────────────
    {"id":"amerisolar-as-6m-335","marca":"Amerisolar","modelo":"AS-6M30 335W Mono PERC","potencia_wp":335,"eficiencia":17.2,"tipo":"monocristalino","largura_mm":992,"altura_mm":1960,"espessura_mm":40,"peso_kg":21.0,"garantia_produto_anos":10,"garantia_potencia_anos":25,"potencia_min_25anos":80.70,"corrente_isc":9.78,"tensao_voc":43.60,"url_datasheet":""},

    # ── Znshine Solar ─────────────────────────────────────────────────────────
    {"id":"znshine-zxm7-shld72-550","marca":"Znshine Solar","modelo":"ZXM7-SHLD72-550W HC","potencia_wp":550,"eficiencia":21.1,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":14.02,"tensao_voc":49.50,"url_datasheet":""},

    # ── AE Solar ─────────────────────────────────────────────────────────────
    {"id":"ae-solar-aurora-420","marca":"AE Solar","modelo":"AE420MHM-60DB Aurora Mono","potencia_wp":420,"eficiencia":21.5,"tipo":"half_cell","largura_mm":1046,"altura_mm":1879,"espessura_mm":30,"peso_kg":21.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.27,"tensao_voc":41.14,"url_datasheet":""},
    {"id":"ae-solar-aurora-550","marca":"AE Solar","modelo":"AE550MHM-72DB Aurora HC","potencia_wp":550,"eficiencia":21.1,"tipo":"half_cell","largura_mm":1134,"altura_mm":2278,"espessura_mm":35,"peso_kg":28.0,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.98,"tensao_voc":49.55,"url_datasheet":""},

    # ── Giga Solar / Growatt Modules ──────────────────────────────────────────
    {"id":"growatt-mac-405","marca":"Growatt Modules","modelo":"GMF405MD Half-Cell","potencia_wp":405,"eficiencia":20.8,"tipo":"half_cell","largura_mm":1003,"altura_mm":1979,"espessura_mm":30,"peso_kg":20.5,"garantia_produto_anos":12,"garantia_potencia_anos":25,"potencia_min_25anos":84.80,"corrente_isc":13.03,"tensao_voc":40.30,"url_datasheet":""},

    # ── Yingli Solar (YGE) ────────────────────────────────────────────────────
    {"id":"yingli-yge-380","marca":"Yingli Solar","modelo":"YGE-6A30-380 Panda PERC","potencia_wp":380,"eficiencia":19.6,"tipo":"monocristalino","largura_mm":992,"altura_mm":1956,"espessura_mm":40,"peso_kg":20.8,"garantia_produto_anos":10,"garantia_potencia_anos":25,"potencia_min_25anos":80.70,"corrente_isc":10.50,"tensao_voc":47.54,"url_datasheet":""},
]

# ---------------------------------------------------------------------------
# Inversores solares
# ---------------------------------------------------------------------------

class InversorSolar(TypedDict):
    id: str
    marca: str
    modelo: str
    potencia_kw: float
    tipo: str           # string | micro | hibrido | off_grid | central
    fases: int          # 1 | 3
    eficiencia_max: float  # %
    tensao_mppt_min: int
    tensao_mppt_max: int
    num_mppt: int
    corrente_cc_max: float  # A por MPPT
    tensao_saida_v: int     # 220 | 380
    garantia_anos: int
    comunicacao: str        # WiFi | LAN | RS485 | Zigbee
    certificacoes: str


INVERSORES: list[InversorSolar] = [
    # ── Growatt ── String ─────────────────────────────────────────────────────
    {"id":"growatt-min-3000tl3-s","marca":"Growatt","modelo":"MIN 3000TL3-S","potencia_kw":3.0,"tipo":"string","fases":3,"eficiencia_max":98.5,"tensao_mppt_min":90,"tensao_mppt_max":500,"num_mppt":2,"corrente_cc_max":11.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"INMETRO/CE/IEC"},
    {"id":"growatt-min-5000tl3-s","marca":"Growatt","modelo":"MIN 5000TL3-S","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.5,"tensao_mppt_min":90,"tensao_mppt_max":500,"num_mppt":2,"corrente_cc_max":11.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"INMETRO/CE/IEC"},
    {"id":"growatt-min-7600tl3-s","marca":"Growatt","modelo":"MIN 7600TL3-S","potencia_kw":7.6,"tipo":"string","fases":3,"eficiencia_max":98.5,"tensao_mppt_min":90,"tensao_mppt_max":500,"num_mppt":2,"corrente_cc_max":11.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"INMETRO/CE/IEC"},
    {"id":"growatt-mac-15ktl3-xl","marca":"Growatt","modelo":"MAC 15KTL3-X L","potencia_kw":15.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":3,"corrente_cc_max":30.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"growatt-mac-20ktl3-xl","marca":"Growatt","modelo":"MAC 20KTL3-X L","potencia_kw":20.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":4,"corrente_cc_max":30.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"growatt-max-30ktl3-xl","marca":"Growatt","modelo":"MAX 30KTL3 LV","potencia_kw":30.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":4,"corrente_cc_max":32.5,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"growatt-max-50ktl3-xe","marca":"Growatt","modelo":"MAX 50KTL3 XE","potencia_kw":50.0,"tipo":"string","fases":3,"eficiencia_max":98.7,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":6,"corrente_cc_max":32.5,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"growatt-max-80ktl3-xe","marca":"Growatt","modelo":"MAX 80KTL3 XE","potencia_kw":80.0,"tipo":"string","fases":3,"eficiencia_max":98.7,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":8,"corrente_cc_max":32.5,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},

    # ── Growatt ── Híbrido ────────────────────────────────────────────────────
    {"id":"growatt-sph-5000-es","marca":"Growatt","modelo":"SPH 5000TL BL-UP Híbrido","potencia_kw":5.0,"tipo":"hibrido","fases":1,"eficiencia_max":97.6,"tensao_mppt_min":80,"tensao_mppt_max":550,"num_mppt":2,"corrente_cc_max":13.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},
    {"id":"growatt-sph-10000-xl","marca":"Growatt","modelo":"SPH 10000TL3 BH-UP Híbrido","potencia_kw":10.0,"tipo":"hibrido","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":100,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},

    # ── Sungrow ── String ─────────────────────────────────────────────────────
    {"id":"sungrow-sg3.0rt","marca":"Sungrow","modelo":"SG3.0RT","potencia_kw":3.0,"tipo":"string","fases":3,"eficiencia_max":98.4,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":1,"corrente_cc_max":26.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"sungrow-sg5.0rt","marca":"Sungrow","modelo":"SG5.0RT","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.6,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":26.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"sungrow-sg10rt","marca":"Sungrow","modelo":"SG10RT","potencia_kw":10.0,"tipo":"string","fases":3,"eficiencia_max":98.6,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":26.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"sungrow-sg15rt","marca":"Sungrow","modelo":"SG15RT","potencia_kw":15.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":26.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"sungrow-sg25cx-sa","marca":"Sungrow","modelo":"SG25CX-SA","potencia_kw":25.0,"tipo":"string","fases":3,"eficiencia_max":98.9,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":3,"corrente_cc_max":32.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"sungrow-sg50cx-p","marca":"Sungrow","modelo":"SG50CX-P","potencia_kw":50.0,"tipo":"string","fases":3,"eficiencia_max":98.9,"tensao_mppt_min":200,"tensao_mppt_max":1100,"num_mppt":6,"corrente_cc_max":32.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"sungrow-sg110cx","marca":"Sungrow","modelo":"SG110CX","potencia_kw":110.0,"tipo":"string","fases":3,"eficiencia_max":99.0,"tensao_mppt_min":200,"tensao_mppt_max":1100,"num_mppt":11,"corrente_cc_max":32.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"LAN/RS485","certificacoes":"CE/IEC"},

    # ── Sungrow ── Híbrido ────────────────────────────────────────────────────
    {"id":"sungrow-sh5.0rs","marca":"Sungrow","modelo":"SH5.0RS Híbrido","potencia_kw":5.0,"tipo":"hibrido","fases":1,"eficiencia_max":97.7,"tensao_mppt_min":80,"tensao_mppt_max":600,"num_mppt":2,"corrente_cc_max":13.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},
    {"id":"sungrow-sh10rt","marca":"Sungrow","modelo":"SH10RT Híbrido Trifásico","potencia_kw":10.0,"tipo":"hibrido","fases":3,"eficiencia_max":98.4,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},

    # ── Huawei ── String ──────────────────────────────────────────────────────
    {"id":"huawei-sun2000-5ktl-l1","marca":"Huawei","modelo":"SUN2000-5KTL-L1","potencia_kw":5.0,"tipo":"string","fases":1,"eficiencia_max":98.6,"tensao_mppt_min":90,"tensao_mppt_max":560,"num_mppt":2,"corrente_cc_max":13.5,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"INMETRO/CE/IEC"},
    {"id":"huawei-sun2000-10ktl-m1","marca":"Huawei","modelo":"SUN2000-10KTL-M1","potencia_kw":10.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":26.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"huawei-sun2000-20ktl-m3","marca":"Huawei","modelo":"SUN2000-20KTL-M3","potencia_kw":20.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":4,"corrente_cc_max":26.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"huawei-sun2000-50ktl-m3","marca":"Huawei","modelo":"SUN2000-50KTL-M3","potencia_kw":50.0,"tipo":"string","fases":3,"eficiencia_max":99.0,"tensao_mppt_min":200,"tensao_mppt_max":1100,"num_mppt":6,"corrente_cc_max":26.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"LAN/RS485","certificacoes":"CE/IEC"},
    {"id":"huawei-sun2000-100ktl-m1","marca":"Huawei","modelo":"SUN2000-100KTL-M1","potencia_kw":100.0,"tipo":"string","fases":3,"eficiencia_max":99.0,"tensao_mppt_min":200,"tensao_mppt_max":1100,"num_mppt":10,"corrente_cc_max":26.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"LAN/RS485","certificacoes":"CE/IEC"},

    # ── Huawei ── Híbrido ─────────────────────────────────────────────────────
    {"id":"huawei-sun2000-5ktl-m0","marca":"Huawei","modelo":"SUN2000-5KTL-M0 Híbrido","potencia_kw":5.0,"tipo":"hibrido","fases":1,"eficiencia_max":97.8,"tensao_mppt_min":70,"tensao_mppt_max":560,"num_mppt":2,"corrente_cc_max":13.5,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},
    {"id":"huawei-sun2000-10ktl-m2","marca":"Huawei","modelo":"SUN2000-10KTL-M2 Híbrido","potencia_kw":10.0,"tipo":"hibrido","fases":3,"eficiencia_max":98.4,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},

    # ── SMA ── String ─────────────────────────────────────────────────────────
    {"id":"sma-sunny-boy-5-1","marca":"SMA","modelo":"Sunny Boy 5.0","potencia_kw":5.0,"tipo":"string","fases":1,"eficiencia_max":98.1,"tensao_mppt_min":100,"tensao_mppt_max":600,"num_mppt":2,"corrente_cc_max":15.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"INMETRO/CE/IEC"},
    {"id":"sma-sunny-tripower-10","marca":"SMA","modelo":"Sunny Tripower 10.0","potencia_kw":10.0,"tipo":"string","fases":3,"eficiencia_max":98.4,"tensao_mppt_min":150,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":18.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"sma-sunny-tripower-20","marca":"SMA","modelo":"Sunny Tripower 20.0","potencia_kw":20.0,"tipo":"string","fases":3,"eficiencia_max":98.4,"tensao_mppt_min":150,"tensao_mppt_max":800,"num_mppt":3,"corrente_cc_max":18.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"sma-sunny-tripower-smart-25","marca":"SMA","modelo":"Sunny Tripower CORE1 33","potencia_kw":33.0,"tipo":"string","fases":3,"eficiencia_max":98.7,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":6,"corrente_cc_max":27.5,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"LAN/RS485","certificacoes":"CE/IEC"},
    {"id":"sma-sunny-highpower-peak3-100","marca":"SMA","modelo":"Sunny HighPower PEAK3 100","potencia_kw":100.0,"tipo":"string","fases":3,"eficiencia_max":98.7,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":10,"corrente_cc_max":15.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"LAN/RS485","certificacoes":"CE/IEC"},

    # ── SMA ── Híbrido ────────────────────────────────────────────────────────
    {"id":"sma-sunny-boy-storage-6","marca":"SMA","modelo":"Sunny Boy Storage 6.0","potencia_kw":6.0,"tipo":"hibrido","fases":1,"eficiencia_max":97.0,"tensao_mppt_min":80,"tensao_mppt_max":600,"num_mppt":1,"corrente_cc_max":15.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},

    # ── Fronius ── String ─────────────────────────────────────────────────────
    {"id":"fronius-symo-5","marca":"Fronius","modelo":"Symo 5.0-3-M","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":150,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":18.0,"tensao_saida_v":220,"garantia_anos":7,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"fronius-symo-10","marca":"Fronius","modelo":"Symo 10.0-3-M","potencia_kw":10.0,"tipo":"string","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":150,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":18.0,"tensao_saida_v":380,"garantia_anos":7,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"fronius-symo-20","marca":"Fronius","modelo":"Symo 20.0-3-M","potencia_kw":20.0,"tipo":"string","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":150,"tensao_mppt_max":800,"num_mppt":3,"corrente_cc_max":21.0,"tensao_saida_v":380,"garantia_anos":7,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"fronius-symo-gen24-5","marca":"Fronius","modelo":"Symo GEN24 5.0 Plus","potencia_kw":5.0,"tipo":"hibrido","fases":3,"eficiencia_max":97.5,"tensao_mppt_min":50,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":20.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},
    {"id":"fronius-symo-gen24-10","marca":"Fronius","modelo":"Symo GEN24 10.0 Plus","potencia_kw":10.0,"tipo":"hibrido","fases":3,"eficiencia_max":97.5,"tensao_mppt_min":50,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},

    # ── GoodWe ── String ──────────────────────────────────────────────────────
    {"id":"goodwe-gw5k-dt","marca":"GoodWe","modelo":"GW5K-DT","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.3,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":12.5,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"goodwe-gw10k-dt","marca":"GoodWe","modelo":"GW10K-DT","potencia_kw":10.0,"tipo":"string","fases":3,"eficiencia_max":98.5,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"goodwe-gw20k-mt","marca":"GoodWe","modelo":"GW20K-MT","potencia_kw":20.0,"tipo":"string","fases":3,"eficiencia_max":98.5,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":3,"corrente_cc_max":32.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"goodwe-gw50k-mt","marca":"GoodWe","modelo":"GW50K-MT","potencia_kw":50.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1100,"num_mppt":6,"corrente_cc_max":32.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"LAN/RS485","certificacoes":"CE/IEC"},

    # ── GoodWe ── Híbrido ─────────────────────────────────────────────────────
    {"id":"goodwe-et-5k","marca":"GoodWe","modelo":"GW5048-ES Híbrido","potencia_kw":5.0,"tipo":"hibrido","fases":1,"eficiencia_max":97.6,"tensao_mppt_min":80,"tensao_mppt_max":550,"num_mppt":2,"corrente_cc_max":12.5,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},
    {"id":"goodwe-et-10k","marca":"GoodWe","modelo":"GW10048-ET Híbrido Trifásico","potencia_kw":10.0,"tipo":"hibrido","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":80,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},

    # ── Deye ── String ────────────────────────────────────────────────────────
    {"id":"deye-sun-5k-g05","marca":"Deye","modelo":"SUN-5K-G05 String","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.6,"tensao_mppt_min":100,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":12.5,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},
    {"id":"deye-sun-12k-sg","marca":"Deye","modelo":"SUN-12K-SG04LP3 String","potencia_kw":12.0,"tipo":"string","fases":3,"eficiencia_max":98.7,"tensao_mppt_min":100,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},
    {"id":"deye-sun-20k-sg","marca":"Deye","modelo":"SUN-20K-SG01HP3 String","potencia_kw":20.0,"tipo":"string","fases":3,"eficiencia_max":98.7,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":4,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":5,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},
    {"id":"deye-sun-50k-sg","marca":"Deye","modelo":"SUN-50K-SG01HP3 String","potencia_kw":50.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1100,"num_mppt":6,"corrente_cc_max":32.5,"tensao_saida_v":380,"garantia_anos":5,"comunicacao":"LAN/RS485","certificacoes":"CE/IEC"},

    # ── Deye ── Híbrido ───────────────────────────────────────────────────────
    {"id":"deye-sun-5k-sg04-lp1","marca":"Deye","modelo":"SUN-5K-SG04LP1 Híbrido","potencia_kw":5.0,"tipo":"hibrido","fases":1,"eficiencia_max":97.0,"tensao_mppt_min":60,"tensao_mppt_max":500,"num_mppt":2,"corrente_cc_max":12.5,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"WiFi","certificacoes":"CE/IEC"},
    {"id":"deye-sun-8k-sg03-lp1","marca":"Deye","modelo":"SUN-8K-SG03LP1 Híbrido","potencia_kw":8.0,"tipo":"hibrido","fases":1,"eficiencia_max":97.6,"tensao_mppt_min":60,"tensao_mppt_max":500,"num_mppt":2,"corrente_cc_max":13.5,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"WiFi","certificacoes":"CE/IEC"},
    {"id":"deye-sun-10k-sg04-lp3","marca":"Deye","modelo":"SUN-10K-SG04LP3 Híbrido Trifásico","potencia_kw":10.0,"tipo":"hibrido","fases":3,"eficiencia_max":97.8,"tensao_mppt_min":80,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":5,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},

    # ── WEG ── String ─────────────────────────────────────────────────────────
    {"id":"weg-sfw-5000-3","marca":"WEG","modelo":"SFW05000W3BX2S0 5kW Trifásico","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":200,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":11.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE"},
    {"id":"weg-sfw-10000-3","marca":"WEG","modelo":"SFW10000W3BX2S0 10kW Trifásico","potencia_kw":10.0,"tipo":"string","fases":3,"eficiencia_max":98.3,"tensao_mppt_min":200,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":18.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE"},
    {"id":"weg-sfw-20000-3","marca":"WEG","modelo":"SFW20000W3BX4S0 20kW Trifásico","potencia_kw":20.0,"tipo":"string","fases":3,"eficiencia_max":98.4,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":4,"corrente_cc_max":18.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"INMETRO/CE"},

    # ── ABB / FIMER ── String ─────────────────────────────────────────────────
    {"id":"fimer-pvi-5000","marca":"ABB/FIMER","modelo":"PVI-5000-TL-OUTD-S 5kW","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":200,"tensao_mppt_max":900,"num_mppt":2,"corrente_cc_max":18.0,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"RS485/WiFi","certificacoes":"CE/IEC"},
    {"id":"fimer-pvi-10000","marca":"ABB/FIMER","modelo":"PVI-10.0-TL-OUTD-S 10kW","potencia_kw":10.0,"tipo":"string","fases":3,"eficiencia_max":98.2,"tensao_mppt_min":200,"tensao_mppt_max":900,"num_mppt":2,"corrente_cc_max":18.0,"tensao_saida_v":380,"garantia_anos":5,"comunicacao":"RS485/WiFi","certificacoes":"CE/IEC"},
    {"id":"fimer-react2-25","marca":"ABB/FIMER","modelo":"REACT2-UNO-3.6-TL 3.68kW Híbrido","potencia_kw":3.68,"tipo":"hibrido","fases":1,"eficiencia_max":96.5,"tensao_mppt_min":90,"tensao_mppt_max":480,"num_mppt":1,"corrente_cc_max":20.0,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},

    # ── Chint Power (CHNT) ── String ──────────────────────────────────────────
    {"id":"chint-power-svg5kt","marca":"Chint Power","modelo":"SVG5KTL-M1 String","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":100,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":12.5,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},
    {"id":"chint-power-svg15kt","marca":"Chint Power","modelo":"SVG15KTL-MT String","potencia_kw":15.0,"tipo":"string","fases":3,"eficiencia_max":98.3,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":3,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":5,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},
    {"id":"chint-power-svg30kt","marca":"Chint Power","modelo":"SVG30KTL-MT String","potencia_kw":30.0,"tipo":"string","fases":3,"eficiencia_max":98.6,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":4,"corrente_cc_max":32.5,"tensao_saida_v":380,"garantia_anos":5,"comunicacao":"LAN/RS485","certificacoes":"CE/IEC"},

    # ── Sofar Solar ── String ─────────────────────────────────────────────────
    {"id":"sofar-ktl-5k","marca":"Sofar Solar","modelo":"SOFAR 5KTLX-G3","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":160,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":11.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},
    {"id":"sofar-ktl-15k","marca":"Sofar Solar","modelo":"SOFAR 15KTLX-G3","potencia_kw":15.0,"tipo":"string","fases":3,"eficiencia_max":98.4,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":22.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},
    {"id":"sofar-ktl-30k","marca":"Sofar Solar","modelo":"SOFAR 30KTL-G3","potencia_kw":30.0,"tipo":"string","fases":3,"eficiencia_max":98.6,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":4,"corrente_cc_max":22.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"LAN/RS485","certificacoes":"CE/IEC"},

    # ── Sofar Solar ── Híbrido ────────────────────────────────────────────────
    {"id":"sofar-hyd-5k","marca":"Sofar Solar","modelo":"HYD5000-EP Híbrido","potencia_kw":5.0,"tipo":"hibrido","fases":1,"eficiencia_max":97.5,"tensao_mppt_min":80,"tensao_mppt_max":560,"num_mppt":2,"corrente_cc_max":13.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},
    {"id":"sofar-hyd-15k","marca":"Sofar Solar","modelo":"HYD15000-EP Híbrido Trifásico","potencia_kw":15.0,"tipo":"hibrido","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":200,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},

    # ── SolarEdge ── Optimizador ──────────────────────────────────────────────
    {"id":"solaredge-se5k","marca":"SolarEdge","modelo":"SE5K-RW0TEBEN4 + Otimizadores","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":99.0,"tensao_mppt_min":100,"tensao_mppt_max":480,"num_mppt":1,"corrente_cc_max":10.0,"tensao_saida_v":220,"garantia_anos":12,"comunicacao":"WiFi/LAN/ZigBee","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solaredge-se10k","marca":"SolarEdge","modelo":"SE10K-RW0TEBEN4 + Otimizadores","potencia_kw":10.0,"tipo":"string","fases":3,"eficiencia_max":99.0,"tensao_mppt_min":100,"tensao_mppt_max":480,"num_mppt":1,"corrente_cc_max":10.0,"tensao_saida_v":380,"garantia_anos":12,"comunicacao":"WiFi/LAN/ZigBee","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solaredge-se17k","marca":"SolarEdge","modelo":"SE17K-RW0TEBEN4 + Otimizadores","potencia_kw":17.0,"tipo":"string","fases":3,"eficiencia_max":99.2,"tensao_mppt_min":100,"tensao_mppt_max":480,"num_mppt":1,"corrente_cc_max":10.0,"tensao_saida_v":380,"garantia_anos":12,"comunicacao":"WiFi/LAN/ZigBee","certificacoes":"INMETRO/CE/IEC"},

    # ── SolarEdge ── Híbrido ──────────────────────────────────────────────────
    {"id":"solaredge-se5k-rws","marca":"SolarEdge","modelo":"SE5K-RWS Energy Hub Híbrido","potencia_kw":5.0,"tipo":"hibrido","fases":1,"eficiencia_max":99.0,"tensao_mppt_min":100,"tensao_mppt_max":480,"num_mppt":1,"corrente_cc_max":10.0,"tensao_saida_v":220,"garantia_anos":12,"comunicacao":"WiFi/LAN/ZigBee","certificacoes":"CE/IEC"},

    # ── Enphase ── Microinversor ──────────────────────────────────────────────
    {"id":"enphase-iq7plus","marca":"Enphase","modelo":"IQ7+ Microinversor 295W","potencia_kw":0.295,"tipo":"micro","fases":1,"eficiencia_max":97.6,"tensao_mppt_min":27,"tensao_mppt_max":48,"num_mppt":1,"corrente_cc_max":14.0,"tensao_saida_v":220,"garantia_anos":25,"comunicacao":"Envoy/PLC","certificacoes":"INMETRO/CE/IEC"},
    {"id":"enphase-iq8plus","marca":"Enphase","modelo":"IQ8+ Microinversor 330W","potencia_kw":0.330,"tipo":"micro","fases":1,"eficiencia_max":97.7,"tensao_mppt_min":27,"tensao_mppt_max":58,"num_mppt":1,"corrente_cc_max":15.0,"tensao_saida_v":220,"garantia_anos":25,"comunicacao":"Envoy/PLC","certificacoes":"INMETRO/CE/IEC"},
    {"id":"enphase-iq8m","marca":"Enphase","modelo":"IQ8M Microinversor 380W","potencia_kw":0.380,"tipo":"micro","fases":1,"eficiencia_max":97.6,"tensao_mppt_min":27,"tensao_mppt_max":58,"num_mppt":1,"corrente_cc_max":16.0,"tensao_saida_v":220,"garantia_anos":25,"comunicacao":"Envoy/PLC","certificacoes":"INMETRO/CE/IEC"},
    {"id":"enphase-iq8x","marca":"Enphase","modelo":"IQ8X Microinversor 480W","potencia_kw":0.480,"tipo":"micro","fases":1,"eficiencia_max":97.6,"tensao_mppt_min":27,"tensao_mppt_max":58,"num_mppt":1,"corrente_cc_max":20.0,"tensao_saida_v":220,"garantia_anos":25,"comunicacao":"Envoy/PLC","certificacoes":"INMETRO/CE/IEC"},

    # ── Hoymiles ── Microinversor ─────────────────────────────────────────────
    {"id":"hoymiles-hm-600","marca":"Hoymiles","modelo":"HM-600 Microinversor 600W","potencia_kw":0.600,"tipo":"micro","fases":1,"eficiencia_max":96.7,"tensao_mppt_min":16,"tensao_mppt_max":60,"num_mppt":2,"corrente_cc_max":13.5,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"DTU/WiFi","certificacoes":"CE/IEC"},
    {"id":"hoymiles-hm-800","marca":"Hoymiles","modelo":"HM-800 Microinversor 800W","potencia_kw":0.800,"tipo":"micro","fases":1,"eficiencia_max":96.7,"tensao_mppt_min":16,"tensao_mppt_max":60,"num_mppt":2,"corrente_cc_max":13.5,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"DTU/WiFi","certificacoes":"CE/IEC"},
    {"id":"hoymiles-hm-1500","marca":"Hoymiles","modelo":"HM-1500 Microinversor 1500W","potencia_kw":1.500,"tipo":"micro","fases":1,"eficiencia_max":96.5,"tensao_mppt_min":16,"tensao_mppt_max":60,"num_mppt":4,"corrente_cc_max":13.5,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"DTU/WiFi","certificacoes":"CE/IEC"},
    {"id":"hoymiles-hm-2000","marca":"Hoymiles","modelo":"HM-2000 Microinversor 2000W","potencia_kw":2.000,"tipo":"micro","fases":1,"eficiencia_max":96.5,"tensao_mppt_min":16,"tensao_mppt_max":60,"num_mppt":4,"corrente_cc_max":15.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"DTU/WiFi","certificacoes":"CE/IEC"},

    # ── APSystems ── Microinversor ─────────────────────────────────────────────
    {"id":"apsystems-qs1-880","marca":"APSystems","modelo":"QS1 880W Quad-Module","potencia_kw":0.880,"tipo":"micro","fases":1,"eficiencia_max":96.5,"tensao_mppt_min":16,"tensao_mppt_max":55,"num_mppt":4,"corrente_cc_max":13.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"ECU/WiFi","certificacoes":"CE/IEC"},
    {"id":"apsystems-ds3l-960","marca":"APSystems","modelo":"DS3-L 960W Dual-Module","potencia_kw":0.960,"tipo":"micro","fases":1,"eficiencia_max":96.9,"tensao_mppt_min":16,"tensao_mppt_max":58,"num_mppt":2,"corrente_cc_max":16.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"ECU/WiFi","certificacoes":"CE/IEC"},

    # ── Victron Energy ── Off-Grid / Híbrido ──────────────────────────────────
    {"id":"victron-multiplus-ii-3000","marca":"Victron Energy","modelo":"MultiPlus-II 3000VA","potencia_kw":2.4,"tipo":"hibrido","fases":1,"eficiencia_max":96.0,"tensao_mppt_min":0,"tensao_mppt_max":0,"num_mppt":0,"corrente_cc_max":0,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"VE.Bus/Bluetooth","certificacoes":"CE/IEC"},
    {"id":"victron-multiplus-ii-5000","marca":"Victron Energy","modelo":"MultiPlus-II 5000VA","potencia_kw":4.0,"tipo":"hibrido","fases":1,"eficiencia_max":96.0,"tensao_mppt_min":0,"tensao_mppt_max":0,"num_mppt":0,"corrente_cc_max":0,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"VE.Bus/Bluetooth","certificacoes":"CE/IEC"},
    {"id":"victron-quattro-8000","marca":"Victron Energy","modelo":"Quattro 8000VA","potencia_kw":6.4,"tipo":"hibrido","fases":1,"eficiencia_max":96.0,"tensao_mppt_min":0,"tensao_mppt_max":0,"num_mppt":0,"corrente_cc_max":0,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"VE.Bus/Bluetooth","certificacoes":"CE/IEC"},
    {"id":"victron-quattro-15000","marca":"Victron Energy","modelo":"Quattro 15000VA","potencia_kw":12.0,"tipo":"hibrido","fases":1,"eficiencia_max":96.0,"tensao_mppt_min":0,"tensao_mppt_max":0,"num_mppt":0,"corrente_cc_max":0,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"VE.Bus/Bluetooth","certificacoes":"CE/IEC"},

    # ── MUST Solar ── Híbrido / Off-Grid ──────────────────────────────────────
    {"id":"must-ph1800-5k","marca":"MUST Solar","modelo":"PH18-5K48 Híbrido Off-Grid","potencia_kw":5.0,"tipo":"off_grid","fases":1,"eficiencia_max":95.0,"tensao_mppt_min":60,"tensao_mppt_max":450,"num_mppt":1,"corrente_cc_max":80.0,"tensao_saida_v":220,"garantia_anos":2,"comunicacao":"WiFi/RS232","certificacoes":"CE/IEC"},
    {"id":"must-ph3000-5k","marca":"MUST Solar","modelo":"PH3000-5K-PRO Off-Grid","potencia_kw":5.0,"tipo":"off_grid","fases":1,"eficiencia_max":94.0,"tensao_mppt_min":30,"tensao_mppt_max":145,"num_mppt":1,"corrente_cc_max":60.0,"tensao_saida_v":220,"garantia_anos":2,"comunicacao":"WiFi","certificacoes":"CE/IEC"},

    # ── Refusol (AEG Power Solutions) ── String ───────────────────────────────
    {"id":"refusol-one-5k","marca":"Refusol","modelo":"AE 1TL 5.0 String","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":97.6,"tensao_mppt_min":125,"tensao_mppt_max":800,"num_mppt":2,"corrente_cc_max":18.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"RS485/WiFi","certificacoes":"CE/IEC"},
    {"id":"refusol-025k","marca":"Refusol","modelo":"025K String 25kW","potencia_kw":25.0,"tipo":"string","fases":3,"eficiencia_max":98.6,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":3,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"RS485","certificacoes":"CE/IEC"},

    # ── Lenze / SAJ ── String ─────────────────────────────────────────────────
    {"id":"saj-r5-5k","marca":"SAJ","modelo":"R5-5K-T2 String","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.2,"tensao_mppt_min":150,"tensao_mppt_max":850,"num_mppt":2,"corrente_cc_max":11.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},
    {"id":"saj-r5-15k","marca":"SAJ","modelo":"R5-15K-T2 String","potencia_kw":15.0,"tipo":"string","fases":3,"eficiencia_max":98.6,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":3,"corrente_cc_max":22.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},

    # ── Schneider Electric ── Híbrido / Off-Grid ──────────────────────────────
    {"id":"schneider-xw-6848","marca":"Schneider Electric","modelo":"XW+ 6848 Híbrido Off-Grid","potencia_kw":6.8,"tipo":"hibrido","fases":1,"eficiencia_max":95.0,"tensao_mppt_min":0,"tensao_mppt_max":0,"num_mppt":0,"corrente_cc_max":0,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"LAN/RS485","certificacoes":"CE/UL"},
    {"id":"schneider-xw-plus-5548","marca":"Schneider Electric","modelo":"XW+ 5548 Inverter/Charger","potencia_kw":5.5,"tipo":"off_grid","fases":1,"eficiencia_max":94.0,"tensao_mppt_min":0,"tensao_mppt_max":0,"num_mppt":0,"corrente_cc_max":0,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"LAN/RS485","certificacoes":"CE/UL"},

    # ── Solax Power ── String + Híbrido ──────────────────────────────────────
    {"id":"solax-x3-5kw","marca":"Solax Power","modelo":"X3-MIC-5K-G2 String","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":160,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":13.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},
    {"id":"solax-x3-hybrid-5kw","marca":"Solax Power","modelo":"X3-Hybrid-5.0-D Híbrido","potencia_kw":5.0,"tipo":"hibrido","fases":3,"eficiencia_max":97.5,"tensao_mppt_min":80,"tensao_mppt_max":950,"num_mppt":2,"corrente_cc_max":13.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},
    {"id":"solax-x3-hybrid-15kw","marca":"Solax Power","modelo":"X3-Hybrid-15.0-D Híbrido","potencia_kw":15.0,"tipo":"hibrido","fases":3,"eficiencia_max":97.5,"tensao_mppt_min":80,"tensao_mppt_max":950,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},

    # ── Kstar Solar ── String ─────────────────────────────────────────────────
    {"id":"kstar-ktl-5k","marca":"Kstar","modelo":"BluE-S 5KT String","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.1,"tensao_mppt_min":160,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":11.0,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"WiFi/LAN","certificacoes":"CE/IEC"},
    {"id":"kstar-ktl-20k","marca":"Kstar","modelo":"BluE-T 20KT String","potencia_kw":20.0,"tipo":"string","fases":3,"eficiencia_max":98.6,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":3,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":5,"comunicacao":"WiFi/LAN/RS485","certificacoes":"CE/IEC"},

    # ── Ingeteam ── String ────────────────────────────────────────────────────
    {"id":"ingeteam-ingecon-sun-6tl","marca":"Ingeteam","modelo":"INGECON SUN 6TL M-BUS","potencia_kw":6.0,"tipo":"string","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":150,"tensao_mppt_max":850,"num_mppt":2,"corrente_cc_max":18.0,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"RS485/WiFi","certificacoes":"CE/IEC"},
    {"id":"ingeteam-ingecon-sun-20tl","marca":"Ingeteam","modelo":"INGECON SUN 20TL M-BUS","potencia_kw":20.0,"tipo":"string","fases":3,"eficiencia_max":98.5,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":3,"corrente_cc_max":22.0,"tensao_saida_v":380,"garantia_anos":5,"comunicacao":"RS485","certificacoes":"CE/IEC"},

    # ── Delta Electronics ── String ───────────────────────────────────────────
    {"id":"delta-rpi-h5-5k","marca":"Delta","modelo":"RPI H5A 5000 String","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.2,"tensao_mppt_min":200,"tensao_mppt_max":900,"num_mppt":2,"corrente_cc_max":12.5,"tensao_saida_v":220,"garantia_anos":5,"comunicacao":"WiFi/RS485","certificacoes":"CE/IEC"},
    {"id":"delta-rpi-h10-10k","marca":"Delta","modelo":"RPI H10A 10000 String","potencia_kw":10.0,"tipo":"string","fases":3,"eficiencia_max":98.4,"tensao_mppt_min":200,"tensao_mppt_max":900,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":5,"comunicacao":"WiFi/RS485","certificacoes":"CE/IEC"},

    # ── Power Electronics ── Utility ──────────────────────────────────────────
    {"id":"pe-ht-100k","marca":"Power Electronics","modelo":"HT-100K Utility String","potencia_kw":100.0,"tipo":"string","fases":3,"eficiencia_max":99.0,"tensao_mppt_min":450,"tensao_mppt_max":1000,"num_mppt":12,"corrente_cc_max":30.0,"tensao_saida_v":380,"garantia_anos":5,"comunicacao":"LAN/RS485","certificacoes":"CE/IEC"},

    # ── SMA Central ── Central ────────────────────────────────────────────────
    {"id":"sma-sc-200k","marca":"SMA","modelo":"Sunny Central 200 Central","potencia_kw":200.0,"tipo":"central","fases":3,"eficiencia_max":98.7,"tensao_mppt_min":400,"tensao_mppt_max":900,"num_mppt":1,"corrente_cc_max":800.0,"tensao_saida_v":380,"garantia_anos":5,"comunicacao":"LAN/RS485","certificacoes":"CE/IEC"},

    # ── Solis ── String Mono 220V (S5-GR1P / S6-GR1P) ───────────────────────
    {"id":"solis-s6-gr1p-2k","marca":"Solis","modelo":"S6-GR1P2K Mono 220V","potencia_kw":2.0,"tipo":"string","fases":1,"eficiencia_max":97.3,"tensao_mppt_min":80,"tensao_mppt_max":500,"num_mppt":1,"corrente_cc_max":14.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solis-s6-gr1p-3k","marca":"Solis","modelo":"S6-GR1P3K Mono 220V","potencia_kw":3.0,"tipo":"string","fases":1,"eficiencia_max":97.5,"tensao_mppt_min":80,"tensao_mppt_max":500,"num_mppt":1,"corrente_cc_max":14.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solis-s6-gr1p-5k","marca":"Solis","modelo":"S6-GR1P5K Mono 220V","potencia_kw":5.0,"tipo":"string","fases":1,"eficiencia_max":97.7,"tensao_mppt_min":90,"tensao_mppt_max":520,"num_mppt":2,"corrente_cc_max":16.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"INMETRO/CE/IEC"},

    # ── Solis ── String Tri 220V (S5-GR3P / S6-GR3P) ────────────────────────
    {"id":"solis-s6-gr3p-5k","marca":"Solis","modelo":"S6-GR3P5K Tri 220V","potencia_kw":5.0,"tipo":"string","fases":3,"eficiencia_max":98.5,"tensao_mppt_min":90,"tensao_mppt_max":550,"num_mppt":2,"corrente_cc_max":16.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solis-s6-gr3p-8k","marca":"Solis","modelo":"S6-GR3P8K Tri 220V","potencia_kw":8.0,"tipo":"string","fases":3,"eficiencia_max":98.6,"tensao_mppt_min":90,"tensao_mppt_max":550,"num_mppt":2,"corrente_cc_max":21.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solis-s6-gr3p-10k","marca":"Solis","modelo":"S6-GR3P10K Tri 220V","potencia_kw":10.0,"tipo":"string","fases":3,"eficiencia_max":98.7,"tensao_mppt_min":90,"tensao_mppt_max":550,"num_mppt":2,"corrente_cc_max":21.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solis-s5-gr3p-12k","marca":"Solis","modelo":"S5-GR3P12K Tri 220V","potencia_kw":12.0,"tipo":"string","fases":3,"eficiencia_max":98.7,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":26.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solis-s5-gr3p-15k","marca":"Solis","modelo":"S5-GR3P15K Tri 220V","potencia_kw":15.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1000,"num_mppt":2,"corrente_cc_max":26.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"INMETRO/CE/IEC"},

    # ── Solis ── String Tri 380V (S5-GC / S6-GU) ────────────────────────────
    {"id":"solis-s5-gc-20k","marca":"Solis","modelo":"S5-GC20K Tri 380V","potencia_kw":20.0,"tipo":"string","fases":3,"eficiencia_max":98.7,"tensao_mppt_min":180,"tensao_mppt_max":1000,"num_mppt":3,"corrente_cc_max":26.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solis-s5-gc-25k","marca":"Solis","modelo":"S5-GC25K Tri 380V","potencia_kw":25.0,"tipo":"string","fases":3,"eficiencia_max":98.7,"tensao_mppt_min":180,"tensao_mppt_max":1000,"num_mppt":3,"corrente_cc_max":26.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solis-s5-gc-30k","marca":"Solis","modelo":"S5-GC30K Tri 380V","potencia_kw":30.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":180,"tensao_mppt_max":1000,"num_mppt":4,"corrente_cc_max":26.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solis-s5-gc-50k","marca":"Solis","modelo":"S5-GC50K Tri 380V","potencia_kw":50.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1100,"num_mppt":5,"corrente_cc_max":32.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"RS485/LAN","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solis-s6-gc-60k","marca":"Solis","modelo":"S6-GC60K Tri 380V","potencia_kw":60.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1100,"num_mppt":6,"corrente_cc_max":32.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"RS485/LAN","certificacoes":"INMETRO/CE/IEC"},
    {"id":"solis-s6-gc-80k","marca":"Solis","modelo":"S6-GC80K Tri 380V","potencia_kw":80.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1100,"num_mppt":8,"corrente_cc_max":32.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"RS485/LAN","certificacoes":"CE/IEC"},
    {"id":"solis-s6-gc-100k","marca":"Solis","modelo":"S6-GC100K Tri 380V","potencia_kw":100.0,"tipo":"string","fases":3,"eficiencia_max":98.8,"tensao_mppt_min":200,"tensao_mppt_max":1100,"num_mppt":10,"corrente_cc_max":32.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"RS485/LAN","certificacoes":"CE/IEC"},

    # ── Solis ── Híbrido Mono 220V (S6-EH1P) ────────────────────────────────
    {"id":"solis-s6-eh1p-3k","marca":"Solis","modelo":"S6-EH1P3K-L Híbrido Mono","potencia_kw":3.0,"tipo":"hibrido","fases":1,"eficiencia_max":97.5,"tensao_mppt_min":90,"tensao_mppt_max":520,"num_mppt":2,"corrente_cc_max":16.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"CE/IEC"},
    {"id":"solis-s6-eh1p-5k","marca":"Solis","modelo":"S6-EH1P5K-L Híbrido Mono","potencia_kw":5.0,"tipo":"hibrido","fases":1,"eficiencia_max":97.7,"tensao_mppt_min":90,"tensao_mppt_max":520,"num_mppt":2,"corrente_cc_max":16.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"CE/IEC"},
    {"id":"solis-s6-eh1p-6k","marca":"Solis","modelo":"S6-EH1P6K-L Híbrido Mono","potencia_kw":6.0,"tipo":"hibrido","fases":1,"eficiencia_max":97.7,"tensao_mppt_min":90,"tensao_mppt_max":520,"num_mppt":2,"corrente_cc_max":16.0,"tensao_saida_v":220,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"CE/IEC"},

    # ── Solis ── Híbrido Tri (S6-EH3P) ──────────────────────────────────────
    {"id":"solis-s6-eh3p-5k","marca":"Solis","modelo":"S6-EH3P5K-H Híbrido Tri","potencia_kw":5.0,"tipo":"hibrido","fases":3,"eficiencia_max":97.8,"tensao_mppt_min":200,"tensao_mppt_max":850,"num_mppt":2,"corrente_cc_max":16.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"CE/IEC"},
    {"id":"solis-s6-eh3p-10k","marca":"Solis","modelo":"S6-EH3P10K-H Híbrido Tri","potencia_kw":10.0,"tipo":"hibrido","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":200,"tensao_mppt_max":850,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"CE/IEC"},
    {"id":"solis-s6-eh3p-15k","marca":"Solis","modelo":"S6-EH3P15K-L Híbrido Tri","potencia_kw":15.0,"tipo":"hibrido","fases":3,"eficiencia_max":98.0,"tensao_mppt_min":200,"tensao_mppt_max":850,"num_mppt":2,"corrente_cc_max":25.0,"tensao_saida_v":380,"garantia_anos":10,"comunicacao":"WiFi/RS485","certificacoes":"CE/IEC"},
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MODULOS_BY_ID: dict[str, ModuloSolar] = {m["id"]: m for m in MODULOS}
_INVERSORES_BY_ID: dict[str, InversorSolar] = {i["id"]: i for i in INVERSORES}


def get_modulo(modulo_id: str) -> ModuloSolar | None:
    return _MODULOS_BY_ID.get(modulo_id)


def get_inversor(inversor_id: str) -> InversorSolar | None:
    return _INVERSORES_BY_ID.get(inversor_id)


def filtrar_modulos(tipo: str | None = None, potencia_min: int | None = None, potencia_max: int | None = None) -> list[ModuloSolar]:
    result = MODULOS
    if tipo:
        result = [m for m in result if m["tipo"] == tipo]
    if potencia_min is not None:
        result = [m for m in result if m["potencia_wp"] >= potencia_min]
    if potencia_max is not None:
        result = [m for m in result if m["potencia_wp"] <= potencia_max]
    return result


def filtrar_inversores(tipo: str | None = None, potencia_min: float | None = None, potencia_max: float | None = None, fases: int | None = None, marca: str | None = None) -> list[InversorSolar]:
    result = INVERSORES
    if tipo:
        result = [i for i in result if i["tipo"] == tipo]
    if potencia_min is not None:
        result = [i for i in result if i["potencia_kw"] >= potencia_min]
    if potencia_max is not None:
        result = [i for i in result if i["potencia_kw"] <= potencia_max]
    if fases is not None:
        result = [i for i in result if i["fases"] == fases]
    if marca:
        result = [i for i in result if i["marca"].lower() == marca.lower()]
    return result


# ---------------------------------------------------------------------------
# Componentes opcionais (BOS — Balance of System)
# ---------------------------------------------------------------------------

class ComponenteOpcional(TypedDict):
    id: str
    categoria: str          # transformador | string_box | otimizador | estrutura | cabo | protecao | monitoramento
    marca: str
    modelo: str
    descricao: str
    especificacao: str      # potência, tensão, ou dimensão principal
    compatibilidade: str    # "universal" | "marca_especifica"
    preco_referencia: float # R$ estimado (referência, não vinculante)


COMPONENTES_OPCIONAIS: list[ComponenteOpcional] = [
    # ── Transformadores ──────────────────────────────────────────────────────
    {"id":"trafo-15kva-220-380","categoria":"transformador","marca":"WEG","modelo":"Trafo Seco 15kVA 220/380V","descricao":"Transformador isolador trifásico 15kVA para adequação de tensão","especificacao":"15kVA 220/380V","compatibilidade":"universal","preco_referencia":3500.00},
    {"id":"trafo-30kva-220-380","categoria":"transformador","marca":"WEG","modelo":"Trafo Seco 30kVA 220/380V","descricao":"Transformador isolador trifásico 30kVA para adequação de tensão","especificacao":"30kVA 220/380V","compatibilidade":"universal","preco_referencia":5800.00},
    {"id":"trafo-50kva-220-380","categoria":"transformador","marca":"WEG","modelo":"Trafo Seco 50kVA 220/380V","descricao":"Transformador isolador trifásico 50kVA para adequação de tensão","especificacao":"50kVA 220/380V","compatibilidade":"universal","preco_referencia":8500.00},
    {"id":"trafo-75kva-220-380","categoria":"transformador","marca":"WEG","modelo":"Trafo Seco 75kVA 220/380V","descricao":"Transformador isolador trifásico 75kVA para adequação de tensão","especificacao":"75kVA 220/380V","compatibilidade":"universal","preco_referencia":12000.00},
    {"id":"trafo-112kva-220-380","categoria":"transformador","marca":"WEG","modelo":"Trafo Seco 112.5kVA 220/380V","descricao":"Transformador isolador trifásico 112.5kVA para adequação de tensão","especificacao":"112.5kVA 220/380V","compatibilidade":"universal","preco_referencia":16500.00},
    {"id":"trafo-150kva-380-13800","categoria":"transformador","marca":"WEG","modelo":"Trafo Seco 150kVA 380V/13.8kV","descricao":"Transformador elevador para conexão em média tensão","especificacao":"150kVA 380V/13.8kV","compatibilidade":"universal","preco_referencia":28000.00},

    # ── String Boxes ─────────────────────────────────────────────────────────
    {"id":"stringbox-4e-1000v","categoria":"string_box","marca":"ProSolar","modelo":"SB-4E 1000V","descricao":"String box com 4 entradas, fusíveis e DPS CC","especificacao":"4 strings / 1000V / 15A","compatibilidade":"universal","preco_referencia":650.00},
    {"id":"stringbox-8e-1000v","categoria":"string_box","marca":"ProSolar","modelo":"SB-8E 1000V","descricao":"String box com 8 entradas, fusíveis e DPS CC","especificacao":"8 strings / 1000V / 15A","compatibilidade":"universal","preco_referencia":1100.00},
    {"id":"stringbox-16e-1100v","categoria":"string_box","marca":"ProSolar","modelo":"SB-16E 1100V","descricao":"String box com 16 entradas para usinas, fusíveis e DPS CC","especificacao":"16 strings / 1100V / 20A","compatibilidade":"universal","preco_referencia":2200.00},
    {"id":"stringbox-4e-chave","categoria":"string_box","marca":"CLAMPER","modelo":"SB-4E-SEC 1000V","descricao":"String box 4 entradas com chave seccionadora e monitoramento","especificacao":"4 strings / 1000V / 15A + chave","compatibilidade":"universal","preco_referencia":950.00},

    # ── Otimizadores ─────────────────────────────────────────────────────────
    {"id":"solaredge-p505","categoria":"otimizador","marca":"SolarEdge","modelo":"P505 Otimizador 505W","descricao":"Otimizador DC/DC para módulos até 505W","especificacao":"505W / 60V / 12.5A","compatibilidade":"SolarEdge","preco_referencia":280.00},
    {"id":"solaredge-p600","categoria":"otimizador","marca":"SolarEdge","modelo":"P600 Otimizador 600W","descricao":"Otimizador DC/DC para módulos até 600W","especificacao":"600W / 60V / 15A","compatibilidade":"SolarEdge","preco_referencia":320.00},
    {"id":"tigo-ts4-a-o","categoria":"otimizador","marca":"Tigo","modelo":"TS4-A-O Otimizador 700W","descricao":"Otimizador retrofit universal para qualquer inversor string","especificacao":"700W / 80V / 15A","compatibilidade":"universal","preco_referencia":190.00},

    # ── Estruturas de fixação ────────────────────────────────────────────────
    {"id":"estrutura-solo-10mod","categoria":"estrutura","marca":"Romagnole","modelo":"Kit Solo 10 Módulos","descricao":"Estrutura de fixação em solo para 10 módulos em 2 fileiras","especificacao":"10 módulos / alumínio / inclinação ajustável","compatibilidade":"universal","preco_referencia":2800.00},
    {"id":"estrutura-telhado-ceram-10mod","categoria":"estrutura","marca":"Romagnole","modelo":"Kit Telha Cerâmica 10 Módulos","descricao":"Suporte para telhado cerâmico, 10 módulos em trilho","especificacao":"10 módulos / alumínio / trilho","compatibilidade":"universal","preco_referencia":1200.00},
    {"id":"estrutura-telhado-metal-10mod","categoria":"estrutura","marca":"Romagnole","modelo":"Kit Telha Metálica 10 Módulos","descricao":"Suporte para telhado metálico com mini-trilho","especificacao":"10 módulos / alumínio / mini-trilho","compatibilidade":"universal","preco_referencia":900.00},
    {"id":"estrutura-laje-10mod","categoria":"estrutura","marca":"Romagnole","modelo":"Kit Laje 10 Módulos","descricao":"Estrutura triângulo para laje plana, 10 módulos","especificacao":"10 módulos / alumínio / 15°","compatibilidade":"universal","preco_referencia":1600.00},

    # ── Cabos solares CC ─────────────────────────────────────────────────────
    {"id":"cabo-solar-6mm-preto","categoria":"cabo","marca":"Prysmian","modelo":"Cabo Solar 6mm² Preto (100m)","descricao":"Cabo CC solar 6mm², 1.8kV, resistente UV, rolo 100m","especificacao":"6mm² / 1.8kV / 100m / preto","compatibilidade":"universal","preco_referencia":550.00},
    {"id":"cabo-solar-6mm-vermelho","categoria":"cabo","marca":"Prysmian","modelo":"Cabo Solar 6mm² Vermelho (100m)","descricao":"Cabo CC solar 6mm², 1.8kV, resistente UV, rolo 100m","especificacao":"6mm² / 1.8kV / 100m / vermelho","compatibilidade":"universal","preco_referencia":550.00},
    {"id":"cabo-solar-10mm-preto","categoria":"cabo","marca":"Nexans","modelo":"Cabo Solar 10mm² Preto (100m)","descricao":"Cabo CC solar 10mm², 1.8kV, para strings longas","especificacao":"10mm² / 1.8kV / 100m / preto","compatibilidade":"universal","preco_referencia":900.00},

    # ── Proteção e DPS ───────────────────────────────────────────────────────
    {"id":"dps-cc-1000v","categoria":"protecao","marca":"CLAMPER","modelo":"DPS CC 1000V Tipo II","descricao":"Dispositivo de proteção contra surto lado CC, 1000V","especificacao":"1000V / 40kA / Tipo II","compatibilidade":"universal","preco_referencia":320.00},
    {"id":"dps-ca-275v","categoria":"protecao","marca":"CLAMPER","modelo":"DPS CA 275V Tipo II","descricao":"Dispositivo de proteção contra surto lado CA, 275V","especificacao":"275V / 45kA / Tipo II","compatibilidade":"universal","preco_referencia":180.00},
    {"id":"disjuntor-cc-32a-1000v","categoria":"protecao","marca":"ABB","modelo":"Disjuntor CC 32A 1000V","descricao":"Disjuntor bipolar CC para proteção do string box","especificacao":"32A / 1000Vcc / 2P","compatibilidade":"universal","preco_referencia":250.00},

    # ── Monitoramento ────────────────────────────────────────────────────────
    {"id":"datalogger-growatt-shine","categoria":"monitoramento","marca":"Growatt","modelo":"ShineWiFi-X Datalogger","descricao":"Módulo WiFi para monitoramento remoto de inversores Growatt","especificacao":"WiFi 2.4GHz / App ShinePhone","compatibilidade":"Growatt","preco_referencia":150.00},
    {"id":"datalogger-solis-s3","categoria":"monitoramento","marca":"Solis","modelo":"S3-WiFi-ST Datalogger","descricao":"Módulo WiFi para monitoramento remoto de inversores Solis","especificacao":"WiFi 2.4GHz / SolisCloud","compatibilidade":"Solis","preco_referencia":160.00},
    {"id":"medidor-energia-bidi","categoria":"monitoramento","marca":"PZEM","modelo":"Medidor Bidirecional PZEM-004T","descricao":"Medidor de energia bidirecional para controle de injeção","especificacao":"100A / RS485 / Modbus","compatibilidade":"universal","preco_referencia":120.00},
]

_COMPONENTES_BY_ID: dict[str, ComponenteOpcional] = {c["id"]: c for c in COMPONENTES_OPCIONAIS}


def get_componente(componente_id: str) -> ComponenteOpcional | None:
    return _COMPONENTES_BY_ID.get(componente_id)


def filtrar_componentes(categoria: str | None = None, marca: str | None = None, q: str | None = None) -> list[ComponenteOpcional]:
    result = COMPONENTES_OPCIONAIS
    if categoria:
        result = [c for c in result if c["categoria"] == categoria]
    if marca:
        result = [c for c in result if c["marca"].lower() == marca.lower()]
    if q:
        termo = q.lower()
        result = [c for c in result if termo in c["marca"].lower() or termo in c["modelo"].lower() or termo in c["descricao"].lower()]
    return result

