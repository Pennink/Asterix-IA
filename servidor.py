# --- Servidor/API para o Projeto Asterix IA ---
# Versão inicial e simplificada, preparada para a nuvem.

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# --- Armazenamento de Estado Mínimo ---
# Este dicionário guarda o estado atual do robô.
# Numa aplicação real, isto seria um banco de dados.
robot_state = {
    "robot_status": "INATIVO",
    "account_info": { "balance": 0.0, "equity": 0.0, "profit_loss_day": 0.0, "open_positions": 0 },
    "open_position_info": None
}

# --- Rota para servir o painel de controlo ---
# Quando acedemos ao endereço principal, ele serve o nosso index.html.
@app.route('/')
def serve_app():
    return send_from_directory('www', 'index.html')

# --- Rotas da API ---

# O painel e o robô usam esta rota para obter o estado completo.
@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify(robot_state)

# O painel usa esta rota para enviar novas configurações (Ligar/Desligar).
@app.route('/api/config', methods=['POST'])
def set_config():
    global robot_state
    new_config = request.get_json()
    if new_config and 'robot_status' in new_config:
        robot_state["robot_status"] = new_config.get("robot_status")
        print(f"Status do robô alterado para: {robot_state['robot_status']}")
    return jsonify({"message": "Configuração recebida.", "new_state": robot_state})

# O robô usa esta rota para enviar os seus relatórios.
@app.route('/api/report', methods=['POST'])
def report_status():
    global robot_state
    try:
        raw_data = request.data
        # Limpa caracteres nulos que podem vir do MQL5
        clean_data_str = raw_data.decode('utf-8').rstrip('\x00')
        report_data = json.loads(clean_data_str)
        
        if 'account_info' in report_data:
            robot_state['account_info'].update(report_data['account_info'])
            
        robot_state['open_position_info'] = report_data.get('open_position_info', None)
            
        return jsonify({"message": "Relatório recebido."})
    except Exception as e:
        print(f"!!! ERRO AO PROCESSAR /api/report: {e}")
        return jsonify({"error": "Invalid data"}), 400

# O Gunicorn (serviço de nuvem) vai gerir a execução, mas esta parte permite-nos testar localmente.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
