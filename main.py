from model import mCodeGPT
import pandas as pd
import openai
import argparse

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='ontoNxGPT',
        description='Standardize free-text data using ontology',
        epilog='Text at the bottom of help')

    df_ontology = pd.read_excel('mcode_structure.xlsx', sheet_name="Ontology")
    df_prompt = pd.read_excel('mcode_structure.xlsx', sheet_name="Prompt")
    df_promptYesNo = pd.read_excel('mcode_structure.xlsx', sheet_name="Prompt(yesno)")

    parser.add_argument('-i','--input_file', help="Specify the input file for your program. For example, './input_file.txt'")
    parser.add_argument('-k', '--api_key', help="Specify the Azure OpenAI API key for your program. For example, 'f90hsd8jnigkmr3253908yrh7gybfgu93qi4'")
    parser.add_argument('-b', '--api_base', help="Specify the Azure OpenAI base for your program. For example, 'https://deploymentname.openai.azure.com/'")
    parser.add_argument('-v', '--api_version', help="Specify the Azure OpenAI version file for your program, for example, '2023-05-15'")
    parser.add_argument('-d', '--deployment_name', help="Specify the Azure OpenAI deployment name for your program, for example, 'mcodegpt_gpt_35'")
    parser.add_argument('-m', '--method', help="Specify the prompt generating algorithm for your program, for example, 'RLS', 'BFOP', '2POP'")

    args = parser.parse_args()

    with open(args.input_file, 'r') as f:
        input_text = f.read()

    openai.api_key = args.api_key
    openai.api_base = args.api_base  # your endpoint should look like the following
    openai.api_type = 'azure'
    openai.api_version = args.api_version  # this may change in the future
    deployment_name = args.deployment_name   # This will correspond to the custom name you chose for your deployment when you deployed a model.

    model = mCodeGPT(df_ontology, df_prompt, df_promptYesNo, deployment_name, input_text, args.method)

    df_result = model.run()

    df_result.to_csv('./output.csv')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
