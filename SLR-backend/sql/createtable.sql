

-- 切换库
use slr;

-- 用户表
create table if not exists user
(
    id           bigint auto_increment comment 'id' primary key,
    userAccount  varchar(256)                           not null comment '账号',
    userPassword varchar(512)                           not null comment '密码',
    userName     varchar(256)                           null comment '用户昵称',
    userAvatar   varchar(1024)                          null comment '用户头像',
    userProfile  varchar(512)                           null comment '用户简介',
    userRole     varchar(256) default 'user'            not null comment '用户角色：user/admin',
    editTime     datetime     default CURRENT_TIMESTAMP not null comment '编辑时间',
    createTime   datetime     default CURRENT_TIMESTAMP not null comment '创建时间',
    updateTime   datetime     default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    isDelete     tinyint      default 0                 not null comment '是否删除',
    UNIQUE KEY uk_userAccount (userAccount),
    INDEX idx_userName (userName)
    ) comment '用户' collate = utf8mb4_unicode_ci;

ALTER TABLE user ADD COLUMN is_delete TINYINT DEFAULT 0;



CREATE TABLE practice_record (
                                 id           BIGINT AUTO_INCREMENT PRIMARY KEY,
                                 user_id      BIGINT          NOT NULL,
                                 video_url    VARCHAR(255)    NOT NULL,  -- 视频文件存储路径或URL
                                 ai_advice    TEXT,                      -- AI返回的建议内容
                                 predict_json TEXT,                      -- predict原始结果(JSON字符串)
                                 target_text  VARCHAR(100),              -- 练习目标
                                 create_time   DATETIME       DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE sign_word (
                           id BIGINT PRIMARY KEY AUTO_INCREMENT,
                           word VARCHAR(64) NOT NULL,              -- 词汇
                           videoUrl VARCHAR(255) NOT NULL,        -- 视频链接
                           actionDesc TEXT,                       -- 动作说明
                           chineseMeaning VARCHAR(255)           -- 中文释义
);

INSERT INTO sign_word (word, videoUrl, actionDesc, chineseMeaning) VALUES
                                                                          ('情况', 'http://localhost:8000/ptov/000.mp4', '双手五指微曲，掌心相对，在胸前前后交替转动几下，模拟事情变化的样子。', '表示事物的状态或变化的情形。'),
                                                                          ('前途', 'http://localhost:8000/ptov/001.mp4', '一手伸食指，指尖朝前，从太阳穴处向前方划出。', '象征未来的发展道路。'),
                                                                          ('形势', 'http://localhost:8000/ptov/002.mp4', '双手平伸，掌心向下，在胸前由中间向两侧移动，同时手掌下压。', '表现事物发展的态势。'),
                                                                          ('局势', 'http://localhost:8000/ptov/003.mp4', '双手五指并拢，掌心相对，在胸前围成一个圆形，然后向两侧拉开。', '表示局面、态势。'),
                                                                          ('动态', 'http://localhost:8000/ptov/004.mp4', '双手五指微曲，掌心相对，在胸前交替前后移动。', '表现事物运动变化的状态。'),
                                                                          ('形态', 'http://localhost:8000/ptov/005.mp4', '双手拇指与食指成“L”形，其他手指握拳，然后双手相对，从中间向两侧移动，模拟物体轮廓。', '表现事物的形状或表现状态。'),
                                                                          ('声势', 'http://localhost:8000/ptov/006.mp4', '一手五指并拢，掌心向外，从口前向前推出，同时五指张开。', '表示声威和气势。'),
                                                                          ('优势', 'http://localhost:8000/ptov/007.mp4', '左手平伸，掌心向上；右手伸拇指，置于左手掌心上，然后右手拇指向上移动。', '表示有利的形势或地位。'),
                                                                          ('现实', 'http://localhost:8000/ptov/008.mp4', '双手食指伸直，指尖相对，然后分别向两侧移动，同时食指弯曲成钩状。', '表示实际存在的事物。'),
                                                                          ('实际', 'http://localhost:8000/ptov/009.mp4', '同“现实”手势，或者双手握拳，一上一下，上拳敲击下拳。', '强调真实情况。');
-- 依次插入，000010、000011... 以此类推
