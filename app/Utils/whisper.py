from openai import OpenAI
import logging as log

from dotenv import load_dotenv
from database import AsyncSessionLocal

import app.Utils.crud as crud
import json
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
    try:
        instruction = f"""I need a general notification/report about the event mentioned in the given context, presented in JSON format.
        
        For report, please include:
        - A specified headline focusing on the main event.
        - A professional and informative description of the event, based on the provided context.
        - Extract and clearly state only the street address of the event.
        
        Ensure that the report should be provided as a JSON format.
        --------------------
        Below is the given content you have to analyze.
        {context}
        """
        
        response = client.chat.completions.create(
            model='gpt-4-1106-preview',
            max_tokens=2000,
            messages=[
                {'role': 'system', 'content': instruction},
                {'role': 'user', 'content': """
                    Below is the sample output.
                    {
                        "Headline": "Laird Theater Fire Alarm Response",
                        "Description": "On [Date of the Incident], an emergency response was initiated for a fire alarm at the Laird Theater, located at 129-52 Western Avenue. Initially, there was some confusion regarding the exact location of the incident, with an alarm company incorrectly reporting it as Beggars. Upon clarification, the fire department confirmed the correct location as the Laird Theater.
                        Engine 28-13 was dispatched for auto aid, and multiple fire departments were coordinated through county channels. Upon arrival and investigation, the responding units identified the issue as a faulty fire detector and subsequently reset the alarm. All units were cleared to return to their respective stations.
                        No active fire or emergency was found, and the incident was safely resolved. Additionally, the report notes that Engine 21-13 was made aware of a rear marker light issue on their vehicle.
                        ",
                        "Incident Address": "Laird Theater, 129-52 Western Avenue",
                    }
                """}
            ],
            seed=2425,
            temperature = 0.7,
            response_format={"type": "json_object"}
        )
        response_message = response.choices[0].message.content
        
        print("response: ", response_message)
        
        json_response = json.loads(response_message)
        print(json_response)
    except Exception as e:
        print(e)
        print("--------------")
        
        
async def stt_archive(db, purchased_scanner_id, archive_list):
    context = ""
    # for archive in archive_list:
    #     print("archive: ", archive)
    #     transcript = ""
    #     try:
    #         transcript += await ai_translate(archive['filename'])
    #         print("whisper - context: ", transcript)
            
    #         context += transcript
            
    #         await crud.insert_audio(db, archive['filename'], transcript, purchased_scanner_id)
    #     except Exception as e:
    #         log.error(f"Failed to translate file {archive['filename']}")

    audios = await crud.get_audios_by_scanner_id(db, purchased_scanner_id)
    
    for audio in audios:
        context += audio.context + '\n'
    print(context)
    response = await extract_info_from_context(context)
