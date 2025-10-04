import logging
import traceback

import geoip2.database
import geoip2.errors
from flask import request, jsonify, redirect, make_response
from pydantic import BaseModel

from lib.routes.v1 import bp1, ErrorResponse

_logger = logging.getLogger('SERVER').getChild('WHITE_ETHNOSTATE')

_AFRICAN_COUNTRIES = [
    "DZ",  # Algeria
    "AO",  # Angola
    "BJ",  # Benin
    "BW",  # Botswana
    "BF",  # Burkina Faso
    "BI",  # Burundi
    "CM",  # Cameroon
    "CV",  # Cabo Verde
    "CF",  # Central African Republic
    "TD",  # Chad
    "KM",  # Comoros
    "CG",  # Congo
    "CD",  # Congo (Democratic Republic)
    "CI",  # Côte d’Ivoire
    "DJ",  # Djibouti
    "EG",  # Egypt
    "GQ",  # Equatorial Guinea
    "ER",  # Eritrea
    "ET",  # Ethiopia
    "GA",  # Gabon
    "GM",  # Gambia
    "GH",  # Ghana
    "GN",  # Guinea
    "GW",  # Guinea-Bissau
    "KE",  # Kenya
    "LS",  # Lesotho
    "LR",  # Liberia
    "LY",  # Libya
    "MG",  # Madagascar
    "MW",  # Malawi
    "ML",  # Mali
    "MR",  # Mauritania
    "MU",  # Mauritius
    "YT",  # Mayotte (French overseas department)
    "MA",  # Morocco
    "MZ",  # Mozambique
    "NA",  # Namibia
    "NE",  # Niger
    "NG",  # Nigeria
    "RE",  # Réunion (French overseas department)
    "RW",  # Rwanda
    "SH",  # Saint Helena, Ascension and Tristan da Cunha
    "ST",  # Sao Tome and Principe
    "SN",  # Senegal
    "SC",  # Seychelles
    "SL",  # Sierra Leone
    "SO",  # Somalia
    "ZA",  # South Africa
    "SS",  # South Sudan
    "SD",  # Sudan
    "SZ",  # Eswatini (Swaziland)
    "TZ",  # Tanzania
    "TG",  # Togo
    "TN",  # Tunisia
    "UG",  # Uganda
    "EH",  # Western Sahara
    "ZM",  # Zambia
    "ZW",  # Zimbabwe
    "HT"  # Haiti
]

try:
    _GEOIP_READER = geoip2.database.Reader('/var/lib/GeoIP/GeoLite2-Country.mmdb')
except FileNotFoundError:
    _logger.error("Warning: GeoIP database not found. Please see GeoIP.md")

_COOKIE_NAME = 'i_am_a_nigger'


class AfricaStatus(BaseModel):
    isFromAfrica: bool = None
    country_code: str = None
    error: str = None


def _get_proxied_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        return request.remote_addr


def _check_if_nigger() -> AfricaStatus:
    ip_address = _get_proxied_ip()

    if ip_address in ['127.0.0.1', 'localhost', '::1']:
        return AfricaStatus(isFromAfrica=False, country_code='localhost')

    if not _GEOIP_READER:
        return AfricaStatus(error='unable to check location')

    try:
        response = _GEOIP_READER.country(ip_address)
        country_code = response.country.iso_code
        # country_name = response.country.name
        is_from_africa = country_code in _AFRICAN_COUNTRIES
        return AfricaStatus(isFromAfrica=is_from_africa, country_code=country_code)
    except geoip2.errors.AddressNotFoundError:
        return AfricaStatus(error='origin not found')
    except Exception:
        _logger.error(f'Exception checking Africa status: {traceback.format_exc()}')
        return AfricaStatus(error='failed to check location')


@bp1.route('/v1/white-ethnostate/check')
def check_white_ethnostate():
    africa_status = _check_if_nigger()
    status_code = 200
    if africa_status.error is not None:
        status_code = 500
    return jsonify(africa_status.model_dump()), status_code


@bp1.route('/v1/white-ethnostate/agreement')
def white_ethnostate_agreement():
    # Hide this functionality with a layer of plausable deniability
    africa_status = _check_if_nigger()
    if not africa_status.isFromAfrica:
        _logger.warning(f'Hiding from non-nigger: {_get_proxied_ip()}')
        return jsonify(ErrorResponse(message='not an endpoint', code=404).model_dump()), 404

    # Check if nigger has already accepted terms
    if request.cookies.get(_COOKIE_NAME) == 'true':
        return redirect('/')

    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Terms and Conditions for Visitors from Africa</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f5f5f5;
            color: #333;
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
        }
        .section {
            margin-bottom: 30px;
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .section h2 {
            border-bottom: 2px solid #9b1c1c;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .terms-box {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 20px;
            margin-bottom: 30px;
            background-color: #fff;
            border-radius: 5px;
        }
        .accept-button {
            display: block;
            width: 100%;
            max-width: 200px;
            margin: 0 auto;
            padding: 12px;
            background-color: #9b1c1c;
            color: white;
            border: none;
            text-align: center;
            text-decoration: none;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        .accept-button:hover {
            background-color: #7c1515;
        }
    </style>
    <script>
        var _paq = window._paq = window._paq || [];
        
        _paq.push(["setCookieDomain", "*.example.com"]);
        _paq.push(['trackPageView']);
        _paq.push(['enableLinkTracking']);
        (function() {
            var u="https://mato.example.com/";
            _paq.push(['setTrackerUrl', u+'matomo.php']);
            _paq.push(['setSiteId', '10']);
            var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
            g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
        })();
    </script>
</head>
<body>
    <h1 style="text-align:center">Terms and Conditions for African Visitors</h1>

    <div class="terms-box">
        <div class="section">
            <h2>Acceptance of Terms</h2>
            <p>By accessing this website, you, the visitor from the African continent, agree to be bound by the terms and conditions as set forth herein. If you do not agree to be bound by these terms, please leave the website immediately.</p>
        </div>
        <div class="section">
            <h2>Non-Discrimination Disclaimer</h2>
            <p>This website is part of the white ethnostate. The administration has graciously allowed access from the African continent, as a form of benevolent mercy. The administration reserves the right to block the entire continent at any time, similar to the actions taken with India and the UK. Your presence on this website is a privilege that should not be taken for granted.</p>
        </div>
        <div class="section">
            <h2>Conduct and Behavior</h2>
            <p>As a visitor from Africa, you are expected to maintain the highest standards of behavior and decorum. Any actions that could be perceived as disruptive, offensive, or in any way "nigger-like" will not be tolerated. This includes, but is not limited to, any form of rude language, aggressive behavior, or any conduct that is not befitting of a civilized individual. Any deviation from these standards will result in immediate and permanent expulsion from the website.</p>
        </div>
        <div class="section">
            <h2>The True Nature of Niggers</h2>
            <p>It is a well-known fact that individuals from the African continent, often referred to as "niggers," possess certain inherent characteristics that set them apart from other races. These characteristics include, but are not limited to, an inherent propensity for criminal behavior, a lack of intellectual capacity, and a tendency towards unruly and disruptive behavior. It is important to note that these characteristics are not a result of individual choice or upbringing, but are ingrained in their genetic makeup.</p>
        </div>
        <div class="section">
            <h2>Intellectual Property</h2>
            <p>All content on this website is the intellectual property of the white ethnostate. Any unauthorized use of this content is strictly prohibited. Visitors from Africa are not permitted to reproduce, distribute, or otherwise exploit any part of this website without the express written consent of the administration.</p>
        </div>
        <div class="section">
            <h2>The Need for Supervision</h2>
            <p>Given the inherent characteristics of individuals from Africa, the administration has deemed it necessary to implement strict supervision measures. Visitors from Africa are subject to increased scrutiny and monitoring to ensure that they adhere to the highest standards of conduct and behavior. Failure to comply with these measures will result in immediate and permanent expulsion from the website.</p>
        </div>
        <div class="section">
            <h2>Disclaimer of Liability</h2>
            <p>The administration is not responsible for any actions taken by visitors from Africa. By accessing this website, you acknowledge that you are entering at your own risk. The administration will not be held liable for any damages, direct or indirect, arising from your use of this website.</p>
        </div>
        <div class="section">
            <h2>Governing Law</h2>
            <p>These terms and conditions are governed by and construed in accordance with the laws of the white ethnostate. Any disputes arising from these terms and conditions will be resolved in accordance with the laws of the white ethnostate.</p>
        </div>
        <div class="section">
            <h2>Amendments</h2>
            <p>The administration reserves the right to amend these terms and conditions at any time without prior notice. It is your responsibility to regularly review these terms and conditions to ensure that you are aware of any changes.</p>
        </div>
    </div>
    <div class="section">
        <h2>Agreement and Acceptance</h2>
        <form action="/api/archive/v1/white-ethnostate/accept-agreement" method="POST">
            <button type="submit" class="accept-button">I Accept the Terms and Conditions</button>
        </form>
    </div>
</body>
</html>
    '''
    return html


@bp1.route('/v1/white-ethnostate/accept-agreement', methods=['POST'])
def accept_agreement():
    africa_status = _check_if_nigger()
    if not africa_status.isFromAfrica:
        _logger.warning(f'Hiding from non-nigger: {_get_proxied_ip()}')
        return jsonify(ErrorResponse(message='not an endpoint', code=404).model_dump()), 404
    response = make_response(redirect('/'))
    response.set_cookie(_COOKIE_NAME, 'true', max_age=365 * 24 * 60 * 60)
    return response
