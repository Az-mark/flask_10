from qiniu import  Auth,put_data
from flask import current_app
def upload_pic(f1):
    # 需要填写你的 Access Key 和 Secret Key
    access_key = current_app.config.get('QINIU_AK')
    secret_key = current_app.config.get('QINIU_SK')


    bucket_name = current_app.config.get('QINIU_BUCKET')
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间


    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name)
    # # 要上传文件的本地路径
    # localfile = './sync/bbb.jpg'
    ret, info = put_data(token,None, f1.read())
    print(ret)

    return ret.get('key')