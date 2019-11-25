## 登录

- 说明: 登录到志愿北京
- url: /login
- method: POST
- param:
    - 无
- form:
    - uname: String
    - upass: String
- response:
    - code: Integer 成功码
        - 0: 成功
        - 非0: 失败
    - token: String 令牌，用于以后的请求

## 获取项目列表

- 说明: 只能获取团队项目列表
- url: /get_projects
- method: GET
- param:
    - token: String 登录时返回的令牌
- form:
    - 无
- response:
    - 返回的是一个列表, 列表中每个元素有以下字段
    - id: String 活动的id, 即opp_id
    - name: String 活动名称
    - jobs: List
        - jobs列表中的每个元素有以下字段
            - id: String 岗位的id, 即job_id
            - name: String 岗位名称
    
## 获取时长码列表

- 说明: 只对团队账户有效
- url: /get_code_lsit
- method: GET
- param:
    - token: String 登录时返回的令牌
    - opp_id: String 活动id
    - job_id: String 岗位id
- form:
    - 无
- response:
    - 返回的是一个列表, 列表中每个元素有以下字段
    - code: String 时长码
    - time: String 时长, 可解析为浮点数
    - date: String 时长码生成的时间, yyyy-MM-dd格式
    - use: Object 使用情况
        - user: Object 使用者
            - uid: String 使用者id(志愿北京上的id)
            - name: String 使用者姓名
        - date: String 使用日期(yyyy-MM-dd格式, 未使用时, 该字段取值为'-')

## 生成时长码

- 说明: 单纯的生成操作，不返回时长码
- url: /generate_code
- method: POST
- param:
    - token: String 登录时返回的令牌
- form:
    - opp_id: String 活动id
    - job_id: String 岗位id
    - count: Integer 时长码个数
    - time: Float 时长
    - memo: String 备注
- response:
    - code: Integer
        - 0: 成功
        - 非0: 失败

## 使用时长码

- 说明: 只对志愿者有效
- url: /use_code
- method: POST
- param:
    - token: String 登录时返回的令牌
- form:
    - code: String 时长码
- response:
    - code: Intger
        - 0: 成功
        - 非0: 失败

## 获取我的项目

- 说明: 此接口获取的是志愿者的项目
- url: /my_projects
- method: GET
- param:
    - token: String 登录时返回的令牌
- form:
    - 无
- response:
    - 返回的是项目列表, 列表中每个元素有以下字段
    - id: String 活动id, 即opp_id
    - name: String 活动名称
    - group: String 项目团体
    - date: String 加入日期, yyyy-MM-dd
    - status: String 状态
    - job: String 岗位
    - time: String 服务时长, 可转浮点数

## 获取我的服务时长

- 说明: 获取志愿者服务时长页面表格中的数据
- url: /my_hour
- method: GET
- param:
    - token: String 登录时返回的令牌
- form:
    - 无
- response:
    - 返回的是项目列表, 列表中每个元素有以下字段
    - time: String 服务时长, 可转浮点数
    - description: String 时长下面的描述文字
    - method: String 录入方式
    - status: String 状态
    - opp_id: 活动id
    - name: 活动名称
    - team_id: 团队id
    - team: 团队名称
    - datetime: String 日期和时间, yyyy-MM-dd hh:mm:ss
