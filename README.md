# k8s-deployment-controller
## 概要
k8s-deployment-controllerは、デプロイ元とデプロイ先が異なる端末間でもkubernetesのデプロイを制御できるようにするマイクロサービスです。

## 動作環境
k8s-deployment-controllerは、aion-coreのプラットフォーム上での動作を前提としています。 使用する際は、事前に下記の通りAIONの動作環境を用意してください。
- Kubernetes   
- AION のリソース（Aion-Coreのpython-base-imagesのビルドが必要）   

## セットアップ
1. 本マイクロサービスをクローンする。
2. 本マイクロサービスがクローンされているディレクトリ直下で、下記コマンドを実行し、イメージをビルドする。
    ```
    sh docker-build.sh
    ```

### ※ デプロイ元とデプロイ先が異なる端末の場合 ###
デプロイ元とデプロイ先が異なる端末の場合は、別途セットアップが必要になります。

#### 【 I.デプロイ元とデプロイ先の間でTLS通信ができるようにする方法】
1. デプロイ元でTLSの証明書を作成し、デプロイ先にも証明書を保存する。
2. TLS通信ができるようになると、デプロイ先からデプロイ元のDocker Registryにログインできるようになる。   
    ログインできるかどうかの確認方法
    ```
    docker login {ip}:{port}
    # ip は、デプロイ元のIPを指定する。
    ```
3. ログインできない場合、docker daemonの再起動を行う。
    ```
    sudo systemctl restart docker
    ```
4. ログインできれば、デプロイ元からイメージを Pull できるようになる。ただし、デプロイ元の Docker Registry にイメージが登録されている前提。
    docker pull コマンド
    ```
    docker pull {ip}:{port}/{image}/{tag}
    ```

#### 【 II.ServiceAccountを作成する】
5. k8s-deployment-controller-kubeディレクトリ直下で実行する。
    ```
    $ kubectl apply -f k8s/role.yml
    ```

#### 【 III.Namespaceを作成する】
6. k8s-deployment-controller-kubeディレクトリ直下で実行する。
    ```
    $ PROJECT_SYMBOL="プロジェクトのシンボル名"
    $ kubectl create namespace ${PROJECT_SYMBOL}
    ```
    ※現状は、ユーザプロジェクトはprj 1つのため、プロジェクトのシンボル名は"prj"の固定値を入力する。

#### 【 IV.Secretsを作成する】
7. k8s-deployment-controller-kubeディレクトリ直下で実行する。
    ```
    $ REMOTE_DEVICE_NAME="デプロイ元のデバイス名"
    $ REMOTE_ADDR="デプロイ元のIP:31112"
    $ kubectl create secret docker-registry ${REMOTE_DEVICE_NAME}-registry --docker-server=${REMOTE_ADDR} --docker-username=aion --docker-password=aion -n ${PROJECT_SYMBOL}
    $ kubectl patch sa default -p "{\"imagePullSecrets\": [{\"name\": \"${REMOTE_DEVICE_NAME}-registry\"}]}" -n ${PROJECT_SYMBOL}
    ```
    ※Secretsはデプロイ元となる端末の数だけ作成する必要がある。
