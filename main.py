from with_llm.agent import FNOLLLMAgent
from without_llm.agent import FNOLAgent
from helper.pdfread import readpdf

import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# read API key
API_KEY = os.getenv("API_KEY")

# toggle LLM usage
USE_LLM = True

def main():
    # read FNOL pdf - add your file path
    text = readpdf("sample.pdf")

    if USE_LLM:
        # run LLM based agent
        if not API_KEY:
            raise RuntimeError("API_KEY not set")
        agent = FNOLLLMAgent()
        result = agent.process(text)
    else:
        # run rule based agent
        agent = FNOLAgent()
        result = agent.process(text)

    # print result
    print(result)

if __name__ == "__main__":
    main()
