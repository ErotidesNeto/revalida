from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
import json
import dotenv

dotenv.load_dotenv()

def revalida(file_path_peticao_inicial):
    prompt_template = PromptTemplate.from_template(
        """
        O documento abaixo é uma petição inicial de um processo judicial. Resposta as perguntas apresentadas logo depois do texto.

        <petição inicial>
        {peticao_inicial}
        <\petição inicial>

        Responda no formato de JSON:

        
            "revalidacao": True/False, # Verifique se o caso se trata de mandando de segurança no qual a parte impetrante alega que é médica formada em curso de instituição estrangeira acreditado no Sistema ARCU-SUL e teve seu requerimento administrativo para revalidação de seu diploma de forma simplificada negado pela UEPA.
            "nome_autoridade_coatora": "Nome da autoridade que a petição indica como sendo a coatora",
            "cargo_autoridade_coatora": "cargo da autoridade que a petição indica como sendo a coatora",
            "edital_UEPA": "Número do edital da UEPA referido na petição inicial que rege o processo de Revalidação de Diplomas de graduação do Curso de Medicina, expedidos por Universidades Estrangeiras. Por exemplo, Edital 35/2022-UEPA", Se não houver, retorne None
            "kelly_guedes": True/False, # Verifique se o advogado da petição inicial se chama Kelly Guedes, se sim, retorne True, se não, retorne False
        

        """
    )

    loader = PyPDFLoader(file_path_peticao_inicial)
    
    arquivo = loader.load()    
       
    texto_peticao_inicial = ''
    
    for page in arquivo:
        texto_peticao_inicial+=page.page_content

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

    chain=prompt_template|llm|StrOutputParser()

    #verificar se o arquivo é menor que 31 páginas
    if len(arquivo)<31:
        resposta_chain=chain.invoke({'peticao_inicial': texto_peticao_inicial})    
        
    else: 
        raise ValueError ("Erro: o arquivo da petição inicial não pode ter mais que 30 páginas")

    return json.loads(resposta_chain.replace('```json\n','').replace('\n```',''))

if __name__ == "__main__": 
    print(revalida('.\documentos para teste\PETIÇÃO INICIAL REVALIDA 1.pdf'))
