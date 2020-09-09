from kubernetes import client, config, utils
import json
import time



def main():
    config.load_kube_config()

    v1 = client.CoreV1Api()
    # print("Listing pods with their IPs:")
    # ret = v1.list_pod_for_all_namespaces(watch=False)
    # for i in ret.items:
    #     print("%s\t%s\t%s" %
    #           (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

def create_job(file_path):
    api = client.ApiClient()
    namespace = 'default'

    try:     
        utils.create_from_yaml(api, file_path, namespace=namespace)
    except utils.FailToCreateError as e:
        print("already exists")


    batch = client.BatchV1Api()
    job = batch.read_namespaced_job(name="job-wq-2", namespace=namespace)
    controller_uid = job.metadata.labels["controller-uid"]

    core = client.CoreV1Api()

    pod_label_selector = "controller-uid=" + controller_uid
    pods_list = core.list_namespaced_pod(namespace=namespace, label_selector=pod_label_selector)
    pods = pods_list.items
    for p in pods:
        pod = p.metadata.name
        print(pod)
        try:
            pod_log_response = core.read_namespaced_pod_log(name=pod, namespace=namespace, _return_http_data_only=True, _preload_content=False)
            pod_log = pod_log_response.data
            data = json.loads(pod_log)
            print(data)
        except client.rest.ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced_pod_log: %s\n" % e)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
    file_path = "job.yaml"
    create_job(file_path)
