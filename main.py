from rest.api import Server

if __name__ == "__main__":
    host = "192.168.1.7"
    port = 5000
    server_path = "./temp"
    detector_config_path = "domain/config/cascade_mask_rcnn_hrnetv2p_w32_20e.py"
    detector_model_path ="domain/table_analysis/model/epoch_36.pth"
    
    domain_controller = DomainController(server_path, detector_config_path, detector_model_path)
    server = Server(host, port, path, domain_controller)

    server.start()
