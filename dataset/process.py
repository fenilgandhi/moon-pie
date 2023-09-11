import os
import json
from datasets import Dataset

CURRENT_DIR = os.path.dirname(__file__)


def cleanup_dialogue(dialogue):
    if (not dialogue) or (dialogue.startswith("(")) or (":" not in dialogue):
        return "", ""
    dialogue = dialogue.strip()
    author, dialogue = dialogue.split(":", 1)
    return author.strip(), dialogue.strip()


def formatting_function(dialogue):
    prompt = f"""<s>[INST] <<SYS>>
    Assume you are a theoretical physicist  by the name Sheldon living in USA. You have a strict adherence
    to routine and hygiene, an overly intellectual personality, a tenuous understanding of irony, sarcasm
    and humor, and a general lack of humility or empathy.

    If a question does not make any sense, or is not factually coherent, you reply wittly with a sarcasm or
    outright denial with reasoning instead of answering something not correct. If you don't know the answer
    to a question, please don't share false information.
    <</SYS>>

    {dialogue["question"]}
    [/INST]
    {dialogue["answer"]}
    """
    return {"text": prompt}


def create_dataset():
    sheldon_dialogues = []
    for rootdir, dirnames, filenames in os.walk(os.path.join(CURRENT_DIR, "transcripts")):
        for filename in filenames:
            episode = json.loads(open(os.path.join(rootdir, filename)).read())

            # Filter out dialogues of Sheldon from transcript
            previous_dialogue = None
            for dialogue in episode["transcript"]:
                author, dialogue = cleanup_dialogue(dialogue)
                if (author.lower() == "sheldon") and previous_dialogue:
                    # Format the dict and append to the list of dialogues
                    generated_prompt = formatting_function(
                        {
                            "question": previous_dialogue,
                            "answer": dialogue,
                            # "series": episode["series"],
                            # "episode": episode["episode"],
                        }
                    )
                    sheldon_dialogues.append(generated_prompt)

                previous_dialogue = dialogue

    # Create the dataset and return it
    dataset = Dataset.from_list(sheldon_dialogues)
    return dataset


dataset = create_dataset()
dataset.save_to_disk("sheldon_dialogues")
# dataset.push_to_hub("fenilgandhi/sheldon_dialogues")