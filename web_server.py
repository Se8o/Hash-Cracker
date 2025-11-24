#!/usr/bin/env python3
"""
Simple web server for Parallel Hash Cracking Engine UI
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
import tempfile
from urllib.parse import urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import HashCrackingPipeline
from src.config_loader import ConfigLoader


# Load web server configuration
def load_web_config():
    """Load web server configuration"""
    config_path = 'web_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'server': {'host': 'localhost', 'port': 8080},
        'paths': {
            'html_file': 'web/index.html',
            'temp_csv_prefix': 'temp_input',
            'temp_config_prefix': 'temp_config'
        },
        'output': {
            'log_path': 'logs/web_hasher.log',
            'results_path': 'logs/web_results.json'
        },
        'defaults': {'encoding': 'utf-8', 'worker_timeout': 5}
    }

WEB_CONFIG = load_web_config()


class HashServerHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Serve HTML page and CSS file"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_file = WEB_CONFIG['paths']['html_file']
            with open(html_file, 'rb') as f:
                self.wfile.write(f.read())
        elif parsed_path.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            
            css_file = 'web/style.css'
            with open(css_file, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle API requests"""
        if self.path == '/api/run':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                csv_data = data.get('csv_data', '')
                config = data.get('config', {})
                
                result = self.run_pipeline(csv_data, config)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {
                    'success': False,
                    'error': str(e)
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def run_pipeline(self, csv_data, config):
        """Run the hash cracking pipeline"""
        encoding = WEB_CONFIG['defaults']['encoding']
        csv_prefix = WEB_CONFIG['paths']['temp_csv_prefix']
        config_prefix = WEB_CONFIG['paths']['temp_config_prefix']
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', 
                                         prefix=csv_prefix, encoding=encoding) as csv_file:
            csv_file.write(csv_data)
            csv_path = csv_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json',
                                         prefix=config_prefix, encoding=encoding) as config_file:
            config['input']['csv_path'] = csv_path
            config['output']['log_path'] = WEB_CONFIG['output']['log_path']
            config['output']['results_path'] = WEB_CONFIG['output']['results_path']
            json.dump(config, config_file, indent=2)
            config_path = config_file.name
        
        try:
            pipeline = HashCrackingPipeline(config_path)
            
            import time
            start_time = time.time()
            success = pipeline.run()
            total_time = time.time() - start_time
            
            results_path = config['output']['results_path']
            results_data = []
            
            if os.path.exists(results_path):
                with open(results_path, 'r', encoding='utf-8') as f:
                    results_json = json.load(f)
                    results_data = results_json.get('matches', [])
            
            log_path = config['output']['log_path']
            log_content = ''
            
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    log_content = f.read()
            
            stats = pipeline.receiver.get_statistics()
            
            return {
                'success': success,
                'matches_found': len(results_data),
                'results': results_data,
                'time': total_time,
                'log': log_content,
                'stats': {
                    'total_items': stats['valid_lines'],
                    'matches_found': len(results_data),
                    'total_time': total_time,
                    'rate': stats['valid_lines'] / total_time if total_time > 0 else 0
                }
            }
        
        finally:
            if os.path.exists(csv_path):
                os.unlink(csv_path)
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def log_message(self, format, *args):
        """Custom log message"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Start web server"""
    host = WEB_CONFIG['server']['host']
    port = WEB_CONFIG['server']['port']
    server_address = (host, port)
    httpd = HTTPServer(server_address, HashServerHandler)
    
    print("=" * 60)
    print("Parallel Hash Cracking Engine - Web UI")
    print("=" * 60)
    print(f"\nServer running at: http://{host}:{port}")
    print("Press Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        httpd.server_close()


if __name__ == '__main__':
    main()
