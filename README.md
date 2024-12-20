# Lab4

![image-20241220081229891](C:\Users\ROG\AppData\Roaming\Typora\typora-user-images\image-20241220081229891.png)

新建环境

```
python -m venv producting
```

进入环境

```
cd producting/Scripts
activate
```

安装后端依赖

```
cd ../
pip install -r package.txt
```

查看依赖是否安装完成

```
pip list
```

让后端跑起来

```
uvicorn main:app --reload
```