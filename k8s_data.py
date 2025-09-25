import os
from kubernetes import client, config

class K8SData:
    def __init__(self, kubeconfig=None):
        self.kubeconfig = kubeconfig
        self._load_config()

    def _load_config(self):
        if self.kubeconfig and os.path.exists(self.kubeconfig):
            config.load_kube_config(config_file=os.path.abspath(self.kubeconfig))
        else:
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config()

    def get_node_to_json(self):
        v1 = client.CoreV1Api()
        node_list = v1.list_node()
        data = []
        for node in node_list.items:
            node_dict = client.ApiClient().sanitize_for_serialization(node)
            data.append(node_dict)
        return data

    def get_all_container_configs(self):
        v1 = client.CoreV1Api()
        namespaces = v1.list_namespace()
        all_containers = []

        for ns in namespaces.items:
            namespace = ns.metadata.name
            pods = v1.list_namespaced_pod(namespace=namespace)
            for pod in pods.items:
                pod_name = pod.metadata.name
                containers = pod.spec.containers
                for container in containers:
                    container_dict = client.ApiClient().sanitize_for_serialization(container)
                    container_dict['namespace'] = namespace
                    container_dict['pod_name'] = pod_name
                    all_containers.append(container_dict)
        return all_containers