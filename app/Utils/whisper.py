from openai import OpenAI
import logging as log

from dotenv import load_dotenv
from database import AsyncSessionLocal

import app.Utils.crud as crud
import json
from app.Utils.validate_address import validate_address

load_dotenv()

client = OpenAI()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def ai_translate(audio_file_path):
    # model = whisper.load_model("medium.en")
    # print(f"STT for {audio_file_path}")
    # result = model.transcribe(audio_file_path, fp16=False)

    # pprint(result)
    # something not good here
    print(audio_file_path)
    audio_file= open(audio_file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        language="en"
    )
    
    print(f"STT DONE for {audio_file_path}")
    return transcription.text

async def extract_info_from_context(context):
    functions = [
        {
            "name": 'extract_info',
            "description": "Get the list of notifications/reports about the events mentioned in the given context",
            'parameters': {
                'type': "object",
                "properties":{
                    "event":{
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'Headline': {
                                    'type': 'string',
                                    'description': "A specified headline focusing on the main event."
                                },
                                "Description": {
                                    'type': 'string',
                                    'description': "Over 5 sentences (over 200 words) of professional and informative description of the event, based on the provided context. This description should be provided in detail with over 5 sentences only based on the context."
                                },
                                "Incident_Address": {
                                    'type': 'string',
                                    'description': "Extract and clearly state the formatted street address of the event from the provided text. Make sure the address is as standardized and structured as possible, ideally including street number, street name, city, state, and ZIP code."
                                },
                            }
                        },
                        "required": ["Headline", "Description", "Incident_Address"]
                    }
                }
            },
            "required": ["event"]
        }
    ]
    
    try:
        instruction = f"""I need a general notification/report about the event mentioned in the given context, presented in JSON format."""
        
        response = client.chat.completions.create(
            model='gpt-4o',
            max_tokens=4000,
            messages=[
                {'role': 'system', 'content': instruction},
                {'role': 'user', 'content': f"""
                    This is the input context you have to analyze.
                    {context}
                """}
            ],
            seed=2425,
            temperature = 0.7,
            functions=functions,
            function_call={"name": "extract_info"}
        )
        response_message = response.choices[0].message
        system_fingerprint = response.system_fingerprint
        print(system_fingerprint)

        if hasattr(response_message, "function_call"):
            json_response = json.loads(
                response_message.function_call.arguments)
            print("json_response: ", json_response)
            return json_response
        else:
            print("function_call_error!\n")
            return {}
    except Exception as e:
        print(e)
        print("--------------")


async def get_potential_addresses(address):
    try:
        prompt = f"""
            I have an address input that is potentially incomplete or ambiguous.
            I need your assistance to generate multiple complete address suggestions(more than 7) in json based on the provided data.
            After generating these suggestions, I'll need to validate and rank them using an external service (like Google Address Validator). Please help me by performing the following steps for the given address:

            Initial Address Suggestions
            1. Analyze the provided address data.
            2. Generate multiple potential complete addresses based on the possible interpretations and nearby variations.

            Address Input you will base on:
            {address}
        """ + """
            Sample output is below:
            {
                "addresses": [
                    {"address": "1802 W 9th St, Dixon, IL 61021"},
                    {"address": "1802 West Ninth Street, Dixon, IL 61021"}
                ]
            }
        """
        
        response = client.chat.completions.create(
            model='gpt-4o',
            max_tokens=4000,
            messages=[
                {'role': 'system', 'content': "Generate multiple complete address suggestions in json."},
                {'role': 'user', 'content': prompt}
            ],
            seed=2425,
            temperature = 0.7,
            response_format={"type": "json_object"}
        )
        response_message = response.choices[0].message.content
        json_response = json.loads(response_message)
        return json_response
    except Exception as e:
        print(e)
        print("--------------")
        
async def stt_archive(db, purchased_scanner_id):
    context = ""
    audio_list = await crud.get_audio_by_scanner_id(db, purchased_scanner_id)
    for audio in audio_list:        
        print(audio.context)
        context += audio.context

    # audios = await crud.get_audios_by_scanner_id(db, purchased_scanner_id)
    
    # for audio in audios:
    #     context += audio.context + '\n'
    print(context)
    if context =="":
        return
    
    unit = 70000
    start = 0
    
    while start < len(context):
        sub_context = context[start: start + unit + 200]
        start = start + unit
        
        response = await extract_info_from_context(sub_context)
        
        for event in response['event']:
            try:
                alert = await crud.insert_alert(db, purchased_scanner_id, event)
                if event['Incident_Address']:
                    addresses = await get_potential_addresses(event['Incident_Address'])
                    print("addresses: ", addresses)
                    results = validate_address(addresses)
                    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
                    for result in sorted_results:
                        await crud.insert_validated_address(db, result['address'], result['score'], alert.id)
            except Exception as e:
                print(e)
    
    print('-------------------------------------------------------------------')