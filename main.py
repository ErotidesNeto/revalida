import os
import subprocess
import sys
import time
import streamlit as st
from chain_revalida import revalida
from construcao_doc import criar_novo_documento

# Função para salvar arquivos localmente
def save_uploadedfile(uploadedfile, filename):
    with open(filename, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return filename

# Função para limpar arquivos locais
def clear_files(*files):
    for file in files:
        if file and os.path.exists(file):
            os.remove(file)

# Função principal da aplicação Streamlit
def main():
    st.set_page_config(page_title='Tides', layout='centered', initial_sidebar_state='auto')
    
    st.title('Gerador de Informações de MS')
    st.subheader('Revalidação de Diploma de Medicina')
    st.write("Arraste e solte arquivos PDF nas áreas abaixo ou clique em 'Não possui'.")
    
    st.markdown("---")

    # Inicializa os estados da sessão
    if 'peticao_inicial_path' not in st.session_state:
        st.session_state.peticao_inicial_path = None
    if 'show_download_button' not in st.session_state:
        st.session_state.show_download_button = False
    if 'minuta_file_path' not in st.session_state:
        st.session_state.minuta_file_path = None
    if 'generation_time' not in st.session_state:
        st.session_state.generation_time = 0


    # Força a atualização dos widgets de upload de arquivos
    if 'file_uploader_key' not in st.session_state:
        st.session_state.file_uploader_key = 0

    # Área para Petição Inicial
    peticao_inicial_file = st.file_uploader("Petição Inicial (máximo de 30 páginas)", type="pdf", accept_multiple_files=False, key=f"peticao_inicial_{st.session_state.file_uploader_key}")
    if peticao_inicial_file:
        st.session_state.peticao_inicial_path = save_uploadedfile(peticao_inicial_file, 'peticao_inicial.pdf')
        st.success("Petição Inicial carregada com sucesso!")  
    
    

    # Botão para gerar a minuta
    if st.button('Gerar Minuta'):
        if st.session_state.peticao_inicial_path:
            start_time = time.time()
            with st.spinner('Gerando minuta...'):                
                st.session_state.minuta_file_path = criar_novo_documento(revalida(st.session_state.peticao_inicial_path))
                end_time = time.time()
                st.session_state.generation_time = end_time - start_time
                st.session_state.show_download_button = True
                st.success(f'Minuta gerada com sucesso em {st.session_state.generation_time:.2f} segundos!')
        else:
            st.error('Por favor, carregue a petição inicial.')
    
    if st.session_state.show_download_button:
        with open(st.session_state.minuta_file_path, 'rb') as f:
            st.download_button(label="Baixar Minuta", data=f, file_name='minuta.docx', mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    

    # Botão para reiniciar
    if st.button('Reiniciar'):
        clear_files(st.session_state.peticao_inicial_path, st.session_state.minuta_file_path)
        
        # Remove as chaves do estado da sessão
        for key in ['peticao_inicial_path', 'show_download_button', 'minuta_file_path', 'generation_time']:
            if key in st.session_state:
                del st.session_state[key]
        
        # Incrementa a chave para forçar a atualização dos widgets de upload
        st.session_state.file_uploader_key += 1
        
        st.rerun()

if __name__ == '__main__':
    # Verifica se o script está congelado (executável)
    if getattr(sys, 'frozen', False):
        script_path = os.path.join(sys._MEIPASS, 'your_script.py')
        subprocess.run(['streamlit', 'run', script_path])
    else:
        main()
