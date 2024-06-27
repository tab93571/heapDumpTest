## 注意事項
### 有些aws服務不適用免費方案所以測試完記得要把stack刪掉
## 打包流程
1.打包jar檔
``` sh
mvn clean package
```
2.打包成image並推到自己的repository
記得把${docker_username}改成自己帳號
！如果有改code記得要重新mvn clean package
``` sh
docker login
docker build -t ${docker_username}/simple-app --platform linux/amd64 . 
docker tag ${docker_username}/simple-app ${docker_username}/simple-app 
docker push ${docker_username}/simple-app
```

3.到aws cloudformation 點選create stack上傳ecs.yml

![img_2.png](picture/img_2.png)

4.(optional)imageRepository改成自己的image

![img.png](picture/img_12.png)

5.ecsDemoVpcId & subnetIdList選擇自己的vpc ＆ subnets

![img_1.png](picture/img_13.png)

6.一路點擊next，最後按submit

![img_4.png](picture/img_4.png)

7.stack創建成功！

![img_5.png](picture/img_5.png)

8.點選resources可以查看stack所創建的resource
並點選EcsDemoLoadbalancer進入alb console

![img_2.png](picture/img_14.png)

9.複製DNS name這是我們的public domain name

![img_3.png](picture/img_15.png)

10.如果成功就會看到以下畫面

![img_4.png](picture/img_16.png)

11.如果當前有多台機器，他會AWSALB來黏住當前session，把它刪掉就可以就有可能會導到不同的機器

![img_5.png](picture/img_17.png)

12.可以到cloudwatch觀察log

![img_11.png](picture/img_11.png)

13.可以用/cpu這隻API來測試auto scale

![img.png](picture/img_21.png)
![img_1.png](picture/img_18.png)
![img.png](picture/img_19.png)
![img.png](picture/img_20.png)

14.測試完畢刪除資源，到cloudformation點擊剛創建的stack
點擊delete即可把stack內所有資源刪除

![img.png](picture/img12.png)


## ECS 可能會用到指令
停止指定task
``` sh
aws ecs stop-task --cluster ${cluster_name} --task ${task_ARN}
```
檢查 custom_params 是否為自己使用的
- awslogs-region
- subnetsArn
- imageRepository (optional)


