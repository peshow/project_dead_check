# project_dead_check
##一、功能介绍：##

**以读取配置文件的方式，按设定好的任务计划进行自定义监控：**
* 监控进程是否假死：
    根据日志文件大小一段时间内是否变更，及文件ctime是否变更做判断依据
    
* 增量监控日志的异常信息：
    针对大日志文件做到减少监控资源

* 监控进程的运行状态
   

**目录结构：**
* conf：核心配置文件，main.py读取配置文件中的信息完成操作
* var：各项目的变量函数及公共变量
* m_error：自定义异常信息
* base：管理项目的任务调度执行，使用的是APScheudler
* middle：中间函数，现只有命令行参数解析
* func：项目的功能实现
* log：存放日志文件的目录
* requirement.txt：依赖的Python库信息
* sendmail.py：邮件发送文件
* main.py：项目启动文件
 
 
##二、安装及使用：##
**环境准备：**

依赖的python版本:
* python 3.X
    
安装依赖Python库:
* pip install -r requirement.txt
    
    
**配置文件说明：**
* 使用哪个功能就配置哪个配置文件，但邮件发送 mail.conf 必须配置
    
    
**配置邮件发送方：**
```
$ vim conf/mail.conf
{
  email {
    smtp = smtp.163.com      // smtp服务器的URL地址
    port = 25                // smtp服务器的端口
    src = "test@163.com"     // 邮箱账号，也是发送邮件的用户
    password = "XXXXXXXX"    // 邮箱密码
    send_id = "系统管理员"    // 邮件中显示的发件人名称
    }
}
```

**配置进程假死监控：**
```
$ vim conf/settings.conf
global = {                         ## 全局配置段
    recipients = ""                  // 收件人地址，以逗号隔开
    counts_send = ""                 // 连续错误时，邮件发送上限
    scheduler = {                    // 任务调度
        # trigger: interval          // 以间隔时间执行
        # seconds: 3
        # minutes: 30
        # hours: 3
    }
    subj_body = {                  ## 告警时的标题与正文
        ......
    }
}
thread {                           ## 若不设置可继承global中的配置项
  file1 {                          // 线程编号, 可随意定义
    project = "a.log "             // 项目名称
    command = "python a.py"        // 运行的进程命令
    counts_send = 1           
    log_path = "/data/a.log"       // 进程输出的日志路径
    recipients = "test@qq.com" 
    scheduler = {                  ## 线程执行间隔
      trigger = interval
      seconds = 1200               // 按秒 
      }
  }
}
```

**配置日志异常信息监控：**
```
$ vim conf/settings_log.conf
thread {                           ## 若不设置可继承global中的配置项
  file1 {                          // 线程编号, 可随意定义
    project = "a.log"              // 项目名称
    counts_send = 1                // 连续错误时，邮件发送上限
    format = ".%Y-%m-%d"           // 切割的时间格式，仅支持后缀添加
    behind = 2                     // 输出错误信息后 N 行
    log_path = "/data/a.log"       // 进程输出的日志路径
    recipients = "test@qq.com"     // 收件人列表, 以逗号隔开
    patterns = "error"             // 异常信息的匹配正则
    auto_cut = "True"              // 日志是否自动切割
    scheduler = {                  ## 线程执行间隔
      trigger = interval
      seconds = 1200               // 按秒 
      }
  }
}
```

**配置进程存活监控**
```
$ vim conf/settings_alive.conf
thread {                           ## 若不设置可继承global中的配置项
  file1 {                          ## 线程编号, 可随意定义
    project = "Monitor a.py"       // 监控的项目名
    command = "python a.py"        // 运行的进程命令
    recipients = "test@qq.com"
    scheduler = {                  // 配置任务调度，即监控间隔
      trigger = interval
      seconds = 5
      }
  }
```
**启动监控:**
* -m：仅启动日志异常监控
* -d：仅启动进程假死监控
* -i：仅启动进程存活监控
```
nohup python main.py -l -d &
```


**配置示例:**
```
$ vim conf/settings_log.conf
{
  global = { 
    recipients = "XXXX@qq.com" 
    counts_send = 1   
    scheduler = {  
        trigger: interval 
        seconds: 1200
    }
    subj_body = {      
        ......
    }
  }
  thread {
    file1 {                   
      project = "baidu爬虫"     
      command = "python main.py baidu.log"  
      log_path = "/log/baidu.log"
    }
    file2 {
      project = "sogou爬虫"
      command = "python main.py log/sogou.log"
      log_path = "/log/sogou.log"
      scheduler = {
        trigger: interval
        minutes: 3
        hours: 1
    }
}
