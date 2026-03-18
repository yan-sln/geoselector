import json
import urllib.parse
import urllib.request
from qgis.core import QgsApplication, QgsGeometry, QgsJsonUtils

# Initialise QGIS application (required for QgsJsonUtils)
QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Proxy configuration (as per user request)
proxy_handler = urllib.request.ProxyHandler({
    "http": "http://confproxy.proxy.developpement-durable.gouv.fr:8080",
    "https": "http://confproxy.proxy.developpement-durable.gouv.fr:8080",
})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

WFS_BASE_URL = "https://data.geopf.fr/wfs/ows"

def list_sections(code_insee: str) -> list[str]:
    """
    Récupère la liste des sections disponibles pour une commune donnée.
    """
    params = urllib.parse.urlencode({
        "SERVICE": "WFS",
        "VERSION": "2.0.0",
        "REQUEST": "GetFeature",
        "TYPENAME": "CADASTRALPARCELS.PARCELLAIRE_EXPRESS:feuille",
        "PROPERTYNAME": "section",
        "CQL_FILTER": f"code_insee='{code_insee}'",
        "OUTPUTFORMAT": "application/json"
    })
    url = f"{WFS_BASE_URL}?{params}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        sections = set()
        for f in data.get("features", []):
            section = f["properties"].get("section")
            if section:
                sections.add(section)
        return sorted(list(sections))
    except Exception as e:
        print(f"Erreur lors de la liste des sections : {e}")
        return []

def fetch_section_geometry(code_insee: str, section: str) -> QgsGeometry | None:
    """Récupère la géométrie d'une feuille à partir du code INSEE, de la section et du numéro de feuille.
    """
    params = urllib.parse.urlencode({
        "SERVICE": "WFS",
        "VERSION": "2.0.0",
        "REQUEST": "GetFeature",
        "TYPENAME": "CADASTRALPARCELS.PARCELLAIRE_EXPRESS:feuille",
        "PROPERTYNAME": "geom",
        "CQL_FILTER": f"code_insee='{code_insee}' AND section='{section}'",
        "OUTPUTFORMAT": "application/json",
})
    url = f"{WFS_BASE_URL}?{params}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
        # First attempt: use the response as‑is
        features = QgsJsonUtils.stringToFeatureList(raw)
        if not features:
            # Fallback: transform GeoJSON (move possible properties['geom'] to geometry)
            data_dict = json.loads(raw)
            for feat in data_dict.get("features", []):
                props = feat.get("properties", {})
                geom = props.pop("geom", None)
                if geom is not None:
                    feat["geometry"] = geom
            fixed_json = json.dumps(data_dict)
            features = QgsJsonUtils.stringToFeatureList(fixed_json)
        if features:
            return features[0].geometry()
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de la géométrie de la feuille : {e}")
        return None

if __name__ == '__main__':
    code_insee = '59521'  # Exemple : Lille
    sections = list_sections(code_insee)
    print("Sections disponibles :", sections)
    geometry = fetch_section_geometry(code_insee, 'ZC')
    if geometry:
            print("Géométrie de la section récupérée avec succès !")
    else:
        print("Échec de la récupération de la géométrie de la section.")
