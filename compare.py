from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os
from prompt_load import load_prompts
load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")

llm = ChatOpenAI(model_name="gpt-4-turbo", temperature = 0.3, openai_api_key=openai_api_key)

prompt = load_prompts("comparison_prompt")



claim_data = """
{
    "system_header": {
        "screen_type": "EMPLOYEE MASTER",
        "access_level": "REVIEW ONLY",
        "system": "HCS CORRECTIONAL MGMT WELLPATH"
    },
    "group_information": {
        "group_number": "136",
        "group_id": "790136",
        "organization": "PA DOC"
    },
    "employee_details": {
        "identification": {
            "ssn": "997-13-3338",
            "certification_number": "BASLP1830"
        },
        "personal_info": {
            "first_name": "MARTWON",
            "middle_initial": "D",
            "last_name": "JOHNSON",
            "suffix": null
        },
        "demographics": {
            "sex": "M",
            "birthday": "07/20/1992",
            "age": "32"
        },
        "address": {
            "line1": "2500 LISBURN ROAD",
            "line2": null,
            "city": "CAMP HILL",
            "state": "PA",
            "zip": "17001"
        },
        "contact": {
            "work_phone": null,
            "home_phone": null
        },
        "department": {
            "code": "0471",
            "spc_exp_flg": "N"
        }
    },
    "employment_status": {
        "hired_date": null,
        "first_effective_date": "06/09/2021",
        "status_history": [
            {
                "status": "Active",
                "effective_date": "06/09/2021"
            },
            {
                "status": "Termed",
                "effective_date": "02/12/2019"
            },
            {
                "status": "Active",
                "effective_date": "02/01/2017"
            },
            {
                "status": "Active",
                "effective_date": "01/01/2016"
            }
        ]
    },
    "flags_and_indicators": {
        "marital_status": {
            "status": null,
            "married_on": null
        },
        "dependents": "N",
        "medicare": "N",
        "tov": "N",
        "und": "N"
    },
    "requirements": {
        "cards": {
            "required": true,
            "selected": null
        },
        "certs": {
            "required": true,
            "selected": "N"
        },
        "label": {
            "required": true,
            "selected": "N"
        },
        "hipaa": {
            "required": true,
            "selected": "N"
        }
    },
    "associated_claims": {
        "recent_claim": {
            "claim_number": "225-050474-00",
            "service_date": "03/31/25",
            "diagnosis_code": "J01.90",
            "total_charges": 5567.95,
            "total_paid": 0.00,
            "services": [
                {
                    "procedure_code": "36415",
                    "description": "Lab Services",
                    "amount": 26.00,
                    "status": "Processed"
                },
                {
                    "procedure_code": "84484",
                    "amount": 144.00,
                    "status": "Processed"
                },
                {
                    "procedure_code": "83880",
                    "amount": 284.00,
                    "status": "Processed"
                },
                {
                    "procedure_code": "83690",
                    "amount": 55.00,
                    "status": "Processed"
                },
                {
                    "procedure_code": "83605",
                    "amount": 97.00,
                    "status": "Processed"
                },
                {
                    "procedure_code": "80053",
                    "amount": 122.00,
                    "status": "Processed"
                },
                {
                    "procedure_code": "85739",
                    "amount": 49.00,
                    "status": "Processed"
                },
                {
                    "procedure_code": "85610",
                    "amount": 38.00,
                    "status": "Processed"
                },
                {
                    "procedure_code": "85025",
                    "amount": 70.00,
                    "status": "Processed"
                },
                {
                    "procedure_code": "71046",
                    "amount": 298.00,
                    "status": "Processed"
                },
                {
                    "procedure_code": "70486",
                    "amount": 1457.00,
                    "status": "Processed"
                }
            ]
        }
    },
    "system_functions": {
        "available_options": [
            {
                "key": "F6",
                "function": "Notes"
            },
            {
                "key": "F8",
                "function": "HIPAA"
            },
            {
                "key": "F7",
                "function": "COBRA"
            }
        ]
    }
}
"""

def compare_data():
    formatted_prompt = prompt.format(sds_data=sds_data, claim_data=claim_data)
    response = llm.invoke(formatted_prompt)
    return response.content




