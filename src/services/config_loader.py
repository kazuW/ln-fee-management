import os
import configparser

class ConfigLoader:
    def __init__(self, config_file=None):
        self.config = configparser.ConfigParser()
        
        # デフォルトの設定ファイルパス
        if config_file is None:
            # プロジェクトルートディレクトリを検索
            root_dir = self._find_project_root()
            config_file = os.path.join(root_dir, "ln-fee-manager.conf")
        
        # 設定ファイルの読み込み
        if os.path.exists(config_file):
            self.config.read(config_file, encoding='utf-8')
        else:
            raise FileNotFoundError(f"設定ファイル '{config_file}' が見つかりません")
    
    def _find_project_root(self):
        """プロジェクトのルートディレクトリを見つける"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # services ディレクトリの親（src）、さらにその親がプロジェクトルート
        return os.path.abspath(os.path.join(current_dir, "..", ".."))
    
    # データベース関連
    def get_database_file(self):
        return self.config.get('database', 'database_file')
    
    # パス関連
    def get_fixed_channel_list(self):
        return self.config.get('channels', 'fixed_channel_list')
    
    def get_control_channel_list(self):
        return self.config.get('channels', 'control_channel_list')
    
    # API関連
    def get_api_url(self):
        return self.config.get('api', 'api_url')
    
    def get_macaroon_path(self):
        return self.config.get('api', 'macaroon_path')
    
    def get_tls_path(self):
        return self.config.get('api', 'tls_path')
    
    # 手数料関連
    def get_basefee_msat(self):
        return self.config.getint('fees', 'basefee_msat')
    
    def get_time_lock_delta(self):
        return self.config.getint('fees', 'time_lock_delta')
    
    def get_inboundFee_base(self):
        return self.config.getint('fees', 'inboundFee_base')
    
    def get_inboundFee_ratio(self):
        ratio_str = self.config.get('fees', 'inboundFee_ratio')
        return [float(x) for x in ratio_str.split(',')]
    
    def get_LocalFee_ratio(self):
        ratio_str = self.config.get('fees', 'LocalFee_ratio')
        return [float(x) for x in ratio_str.split(',')]
    
    def get_fee_decreasing_threshold(self):
        return self.config.getfloat('fees', 'fee_decreasing_threshold')
    
    # 分析関連
    def get_data_period(self):
        return self.config.getint('analysis', 'data_period')
    
    # デバッグ関連
    def get_debug_mode(self):
        return self.config.getboolean('debug', 'Debug_mode')