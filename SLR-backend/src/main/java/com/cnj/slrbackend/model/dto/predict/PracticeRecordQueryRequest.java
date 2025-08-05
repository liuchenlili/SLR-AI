package com.cnj.slrbackend.model.dto.predict;


import com.cnj.slrbackend.common.PageRequest;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.Date;

/**
 * 用户查询请求
 */
@EqualsAndHashCode(callSuper = true)
@Data
public class PracticeRecordQueryRequest extends PageRequest implements Serializable {

    /**
     * 用户id
     */
    private Long user_id;


    private String target_text;




    private static final long serialVersionUID = 1L;
}
