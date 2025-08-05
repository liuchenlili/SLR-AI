package com.cnj.slrbackend.model.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.util.Date;

/**
 */
@TableName(value ="practice_record")
@Data
public class PracticeRecord implements Serializable {
    private Long id;
    @TableField("user_id")
    private Long userId;
    @TableField("video_url")
    private String videoUrl;
    @TableField("ai_advice")
    private String aiAdvice;
    @TableField("predict_json")
    private String predictJson;
    @TableField("target_text")
    private String targetText;
    @TableField("create_time")
    private Date createTime;


}