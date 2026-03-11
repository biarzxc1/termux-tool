import requests
import uuid
import time
import random
import string
import base64
import secrets
import json
import re
import pyotp


class API:
    def __init__(self, uid, password, twofa_code):
        self.uid = uid
        self.password = password
        self.twofa_code = twofa_code
        self.device_id = str(uuid.uuid4())
        self.machine_id = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=24))
        self.data_ = {"challenge_nonce": base64.b64encode(secrets.token_bytes(32)).decode('utf-8'),"username":f"{uid}"}
        self.nonce_b64 = base64.b64encode(json.dumps(self.data_).encode('utf-8')).decode('utf-8')
        self.hni = random.choice(['45201', '45204', '45202'])

        self.req = self.sessi()

    def sessi(self):
        ses = requests.Session()
        headers = {
            'Host': 'b-graph.facebook.com',
            'X-Fb-Request-Analytics-Tags': '{"network_tags":{"product":"350685531728","request_category":"graphql","purpose":"fetch","retry_attempt":"0"},"application_tags":"graphservice"}',
            'X-Fb-Rmd': 'state=URL_ELIGIBLE',
            'Priority': 'u=0',
            'X-Zero-Eh': secrets.token_hex(32 // 2),
            'User-Agent': '[FBAN/FB4A;FBAV/549.0.0.61.62;FBBV/891620555;FBDM/{density=3.0,width=1080,height=1920};FBLC/vi_VN;FBRV/0;FBCR/MobiFone;FBMF/Samsung;FBBD/Samsung;FBPN/com.facebook.katana;FBDV/SM-N980F;FBSV/9;FBOP/1;FBCA/x86_64:arm64-v8a;]',
            'X-Fb-Friendly-Name': 'FbBloksActionRootQuery-com.bloks.www.bloks.caa.login.async.send_login_request',
            'X-Zero-F-Device-Id': self.device_id,
            'X-Fb-Integrity-Machine-Id': self.machine_id,
            'X-Graphql-Request-Purpose': 'fetch',
            'X-Tigon-Is-Retry': 'False',
            'X-Graphql-Client-Library': 'graphservice',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Fb-Net-Hni': self.hni,
            'X-Fb-Sim-Hni': self.hni,
            'Authorization': 'OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32',
            'X-Zero-State': 'unknown',
            'X-Meta-Zca': 'empty_token',
            'App-Scope-Id-Header': self.device_id,
            'X-Fb-Connection-Type': 'WIFI',
            'X-Meta-Usdid': f"{str(uuid.uuid4())}.{int(time.time())}.{''.join(random.choices(string.ascii_letters + string.digits, k=100))}",
            'X-Fb-Http-Engine': 'Tigon/Liger',
            'X-Fb-Client-Ip': 'True',
            'X-Fb-Server-Cluster': 'True',
            'X-Fb-Conn-Uuid-Client': secrets.token_hex(32 // 2),
        }
        ses.headers.update(headers)
        return ses

    def login(self):
        data = {
            'method': 'post',
            'pretty': 'false',
            'format': 'json',
            'server_timestamps': 'true',
            'locale': 'vi_VN',
            'purpose': 'fetch',
            'fb_api_req_friendly_name': 'FbBloksActionRootQuery-com.bloks.www.bloks.caa.login.async.send_login_request',
            'fb_api_caller_class': 'graphservice',
            'client_doc_id': '119940804211646733019770319568',
            'fb_api_client_context': '{"is_background":false}',
            'variables': '{"params":{"params":"{\\"params\\":\\"{\\\\\\"client_input_params\\\\\\":{\\\\\\"aac\\\\\\":\\\\\\"{\\\\\\\\\\\\\\"aac_init_timestamp\\\\\\\\\\\\\\":'+str(int(time.time()))+',\\\\\\\\\\\\\\"aacjid\\\\\\\\\\\\\\":\\\\\\\\\\\\\\"'+str(uuid.uuid4())+'\\\\\\\\\\\\\\",\\\\\\\\\\\\\\"aaccs\\\\\\\\\\\\\\":\\\\\\\\\\\\\\"KOM4e6kWGcnzkrB5_kx906-l8IAy5zva03VpX__gVn4\\\\\\\\\\\\\\"}\\\\\\",\\\\\\"sim_phones\\\\\\":[],\\\\\\"aymh_accounts\\\\\\":[{\\\\\\"profiles\\\\\\":{\\\\\\"id\\\\\\":{\\\\\\"is_derived\\\\\\":0,\\\\\\"credentials\\\\\\":[],\\\\\\"account_center_id\\\\\\":\\\\\\"\\\\\\",\\\\\\"profile_picture_url\\\\\\":\\\\\\"\\\\\\",\\\\\\"small_profile_picture_url\\\\\\":null,\\\\\\"notification_count\\\\\\":0,\\\\\\"token\\\\\\":\\\\\\"\\\\\\",\\\\\\"last_access_time\\\\\\":0,\\\\\\"has_smartlock\\\\\\":0,\\\\\\"credential_type\\\\\\":\\\\\\"none\\\\\\",\\\\\\"password\\\\\\":\\\\\\"\\\\\\",\\\\\\"from_accurate_privacy_result\\\\\\":0,\\\\\\"dbln_validated\\\\\\":0,\\\\\\"user_id\\\\\\":\\\\\\"\\\\\\",\\\\\\"name\\\\\\":\\\\\\"\\\\\\",\\\\\\"nta_eligibility_reason\\\\\\":null,\\\\\\"username\\\\\\":\\\\\\"\\\\\\",\\\\\\"account_source\\\\\\":\\\\\\"\\\\\\"}},\\\\\\"id\\\\\\":\\\\\\"\\\\\\"}],\\\\\\"network_bssid\\\\\\":null,\\\\\\"secure_family_device_id\\\\\\":\\\\\\"'+str(uuid.uuid4())+'\\\\\\",\\\\\\"attestation_result\\\\\\":{\\\\\\"keyHash\\\\\\":\\\\\\"'+secrets.token_hex(64 // 2)+'\\\\\\",\\\\\\"data\\\\\\":\\\\\\"'+self.nonce_b64+'\\\\\\",\\\\\\"signature\\\\\\":\\\\\\"MEQCIGSSRU91Ft\\\\/RctrQvwzH+d6hFAYnwd6pe1X8IT+s1UldAiBq29Ly4BAJjiYXyq+ruKJK0QPP+NBlhMexIj10Ybhvyg==\\\\\\"},\\\\\\"has_granted_read_contacts_permissions\\\\\\":0,\\\\\\"auth_secure_device_id\\\\\\":\\\\\\"\\\\\\",\\\\\\"has_whatsapp_installed\\\\\\":0,\\\\\\"password\\\\\\":\\\\\\"'+self.password+'\\\\\\",\\\\\\"sso_token_map_json_string\\\\\\":\\\\\\"\\\\\\",\\\\\\"block_store_machine_id\\\\\\":null,\\\\\\"cloud_trust_token\\\\\\":null,\\\\\\"event_flow\\\\\\":\\\\\\"login_manual\\\\\\",\\\\\\"password_contains_non_ascii\\\\\\":\\\\\\"false\\\\\\",\\\\\\"sim_serials\\\\\\":[],\\\\\\"client_known_key_hash\\\\\\":\\\\\\"\\\\\\",\\\\\\"encrypted_msisdn\\\\\\":\\\\\\"\\\\\\",\\\\\\"has_granted_read_phone_permissions\\\\\\":0,\\\\\\"app_manager_id\\\\\\":\\\\\\"null\\\\\\",\\\\\\"should_show_nested_nta_from_aymh\\\\\\":0,\\\\\\"device_id\\\\\\":\\\\\\"'+self.device_id+'\\\\\\",\\\\\\"zero_balance_state\\\\\\":\\\\\\"init\\\\\\",\\\\\\"login_attempt_count\\\\\\":1,\\\\\\"machine_id\\\\\\":\\\\\\"'+self.machine_id+'\\\\\\",\\\\\\"flash_call_permission_status\\\\\\":{\\\\\\"READ_PHONE_STATE\\\\\\":\\\\\\"DENIED\\\\\\",\\\\\\"READ_CALL_LOG\\\\\\":\\\\\\"DENIED\\\\\\",\\\\\\"ANSWER_PHONE_CALLS\\\\\\":\\\\\\"DENIED\\\\\\"},\\\\\\"accounts_list\\\\\\":[],\\\\\\"gms_incoming_call_retriever_eligibility\\\\\\":\\\\\\"not_eligible\\\\\\",\\\\\\"family_device_id\\\\\\":\\\\\\"'+self.device_id+'\\\\\\",\\\\\\"fb_ig_device_id\\\\\\":[],\\\\\\"device_emails\\\\\\":[],\\\\\\"try_num\\\\\\":2,\\\\\\"lois_settings\\\\\\":{\\\\\\"lois_token\\\\\\":\\\\\\"\\\\\\"},\\\\\\"event_step\\\\\\":\\\\\\"home_page\\\\\\",\\\\\\"headers_infra_flow_id\\\\\\":\\\\\\"'+str(uuid.uuid4())+'\\\\\\",\\\\\\"openid_tokens\\\\\\":{},\\\\\\"contact_point\\\\\\":\\\\\\"'+self.uid+'\\\\\\"},\\\\\\"server_params\\\\\\":{\\\\\\"should_trigger_override_login_2fa_action\\\\\\":0,\\\\\\"is_vanilla_password_page_empty_password\\\\\\":0,\\\\\\"is_from_logged_out\\\\\\":0,\\\\\\"should_trigger_override_login_success_action\\\\\\":0,\\\\\\"login_credential_type\\\\\\":\\\\\\"none\\\\\\",\\\\\\"server_login_source\\\\\\":\\\\\\"login\\\\\\",\\\\\\"waterfall_id\\\\\\":\\\\\\"'+str(uuid.uuid4())+'\\\\\\",\\\\\\"two_step_login_type\\\\\\":\\\\\\"one_step_login\\\\\\",\\\\\\"login_source\\\\\\":\\\\\\"Login\\\\\\",\\\\\\"is_platform_login\\\\\\":0,\\\\\\"pw_encryption_try_count\\\\\\":1,\\\\\\"INTERNAL__latency_qpl_marker_id\\\\\\":36707139,\\\\\\"is_from_aymh\\\\\\":0,\\\\\\"offline_experiment_group\\\\\\":\\\\\\"caa_iteration_v6_perf_fb_2\\\\\\",\\\\\\"is_from_landing_page\\\\\\":0,\\\\\\"left_nav_button_action\\\\\\":\\\\\\"BACK\\\\\\",\\\\\\"password_text_input_id\\\\\\":\\\\\\"ngxumu:105\\\\\\",\\\\\\"is_from_empty_password\\\\\\":0,\\\\\\"is_from_msplit_fallback\\\\\\":0,\\\\\\"ar_event_source\\\\\\":\\\\\\"login_home_page\\\\\\",\\\\\\"username_text_input_id\\\\\\":\\\\\\"ngxumu:104\\\\\\",\\\\\\"layered_homepage_experiment_group\\\\\\":null,\\\\\\"device_id\\\\\\":\\\\\\"'+self.device_id+'\\\\\\",\\\\\\"login_surface\\\\\\":\\\\\\"login_home\\\\\\",\\\\\\"INTERNAL__latency_qpl_instance_id\\\\\\":141917525400342,\\\\\\"reg_flow_source\\\\\\":\\\\\\"lid_landing_screen\\\\\\",\\\\\\"is_caa_perf_enabled\\\\\\":1,\\\\\\"credential_type\\\\\\":\\\\\\"password\\\\\\",\\\\\\"is_from_password_entry_page\\\\\\":0,\\\\\\"caller\\\\\\":\\\\\\"gslr\\\\\\",\\\\\\"family_device_id\\\\\\":\\\\\\"'+self.device_id+'\\\\\\",\\\\\\"is_from_assistive_id\\\\\\":0,\\\\\\"access_flow_version\\\\\\":\\\\\\"pre_mt_behavior\\\\\\",\\\\\\"is_from_logged_in_switcher\\\\\\":0}}\\"}","bloks_versioning_id":"afc4edd2a11a4765752ba5790e7db32bd43289d9974f196d1c8f962607950160","app_id":"com.bloks.www.bloks.caa.login.async.send_login_request"},"scale":"3","nt_context":{"using_white_navbar":true,"styles_id":"a32f9cf6373bc5b20b1a2fb57d1c8447","pixel_ratio":3,"is_push_on":true,"debug_tooling_metadata_token":null,"is_flipper_enabled":false,"theme_params":[{"value":[],"design_system_name":"FDS"}],"bloks_version":"afc4edd2a11a4765752ba5790e7db32bd43289d9974f196d1c8f962607950160"}}',
            'fb_api_analytics_tags': '["GraphServices"]',
            'client_trace_id': '6a571623-111c-4914-ac1a-03fc500532ce',
        }

        response = self.req.post('https://b-graph.facebook.com/graphql', data=data).json()
        print(response)
        try:
            full_text = json.dumps(response, ensure_ascii=False)
            eaau_match = re.search(r'EAAAAU[a-zA-Z0-9_-]{100,}', full_text)
            if eaau_match:
                eaau = eaau_match.group(0)
                return eaau

            if 'two_step_verification' in full_text.lower() or 'two_fac' in full_text or 'redirect_two_fac' in full_text:
                context_match = re.search(r'AW[^"]{200,}', full_text)
                if context_match:
                    two_step_verification_context = context_match.group(0).replace('\\', '')
                    print(f"2FA context: {two_step_verification_context}")

                    totp = pyotp.TOTP(self.twofa_code).now()
                    print(f"TOTP code: {totp}")
                    twofa_data = self.twofacode(totp, two_step_verification_context)
                    return twofa_data
                else:
                    return "2FA context not found in response."
            return "Login failed: No EAAAAU token and no 2FA prompt detected."
        except Exception as e:
            print("Login failed:1, error:", str(e))
            return None

    def twofacode(self, code, two_step_verification_context):
        data = {
            'method': 'post',
            'pretty': 'false',
            'format': 'json',
            'server_timestamps': 'true',
            'locale': 'vi_VN',
            'purpose': 'fetch',
            'fb_api_req_friendly_name': 'FbBloksActionRootQuery-com.bloks.www.two_step_verification.verify_code.async',
            'fb_api_caller_class': 'graphservice',
            'client_doc_id': '119940804211646733019770319568',
            'fb_api_client_context': '{"is_background":false}',
            'variables': '{"params":{"params":"{\\"params\\":\\"{\\\\\\"client_input_params\\\\\\":{\\\\\\"auth_secure_device_id\\\\\\":\\\\\\"\\\\\\",\\\\\\"block_store_machine_id\\\\\\":null,\\\\\\"code\\\\\\":\\\\\\"'+code+'\\\\\\",\\\\\\"should_trust_device\\\\\\":1,\\\\\\"family_device_id\\\\\\":\\\\\\"'+self.device_id+'\\\\\\",\\\\\\"device_id\\\\\\":\\\\\\"'+self.device_id+'\\\\\\",\\\\\\"cloud_trust_token\\\\\\":null,\\\\\\"network_bssid\\\\\\":null,\\\\\\"machine_id\\\\\\":\\\\\\"'+self.machine_id+'\\\\\\"},\\\\\\"server_params\\\\\\":{\\\\\\"INTERNAL__latency_qpl_marker_id\\\\\\":36707139,\\\\\\"device_id\\\\\\":\\\\\\"'+self.device_id+'\\\\\\",\\\\\\"spectra_reg_login_data\\\\\\":null,\\\\\\"challenge\\\\\\":\\\\\\"totp\\\\\\",\\\\\\"machine_id\\\\\\":\\\\\\"'+self.machine_id+'\\\\\\",\\\\\\"INTERNAL__latency_qpl_instance_id\\\\\\":144217313000275,\\\\\\"two_step_verification_context\\\\\\":\\\\\\"'+two_step_verification_context+'\\\\\\",\\\\\\"flow_source\\\\\\":\\\\\\"two_factor_login\\\\\\"}}\\"}","bloks_versioning_id":"afc4edd2a11a4765752ba5790e7db32bd43289d9974f196d1c8f962607950160","app_id":"com.bloks.www.two_step_verification.verify_code.async"},"scale":"3","nt_context":{"using_white_navbar":true,"styles_id":"a32f9cf6373bc5b20b1a2fb57d1c8447","pixel_ratio":3,"is_push_on":true,"debug_tooling_metadata_token":null,"is_flipper_enabled":false,"theme_params":[{"value":[],"design_system_name":"FDS"}],"bloks_version":"afc4edd2a11a4765752ba5790e7db32bd43289d9974f196d1c8f962607950160"}}',
            'fb_api_analytics_tags': '["GraphServices"]',
            'client_trace_id': '1f0a5694-1590-4447-bcdb-00fddb1162e1',
        }

        response = self.req.post('https://b-graph.facebook.com/graphql', data=data)
        try:
            full_text = json.dumps(response.json(), ensure_ascii=False)
            eaau_match = re.search(r'EAAAAU[a-zA-Z0-9_-]{100,}', full_text)
            if eaau_match:
                eaau = eaau_match.group(0)
                return eaau
        except Exception as e:
            print("Login failed:2, error:", str(e))
            return None


if __name__ == "__main__":
    uid = "61585015900971"
    password = "09944954574"
    twofa_code = "2SDT4FCWAO33MPQEIP76GKJO6U44BKVI"
    api = API(uid, password, twofa_code)
    print(api.login())
