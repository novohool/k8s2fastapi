##k8s api转成fastapi
给azrg添加非资源权限的访问
kubectl edit ClusterRole azrg-role
- nonResourceURLs:
  - /nodes
  - /containers
  - /auth
  verbs:
  - get

测试是否可以正常访问访问
SECRET=$(kubectl get sa azrg -o jsonpath='{.secrets[0].name}')
TOKEN=$(kubectl get secret $SECRET -o jsonpath='{.data.token}' | base64 -d)
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/nodes