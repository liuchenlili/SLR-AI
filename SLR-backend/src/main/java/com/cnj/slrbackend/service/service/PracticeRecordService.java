package com.cnj.slrbackend.service.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;

import com.cnj.slrbackend.model.dto.predict.PracticeRecordQueryRequest;
import com.cnj.slrbackend.model.dto.user.UserQueryRequest;
import com.cnj.slrbackend.model.entity.PracticeRecord;
import com.cnj.slrbackend.model.entity.User;

/**
 * 针对表【practice_record(练习记录)】的数据库操作Service
 *
 * @author chenxiangwei
 * @createDate 2025-07-07
 */
public interface PracticeRecordService extends IService<PracticeRecord> {


    boolean saveRecord(PracticeRecord record);
    List<PracticeRecord> listRecordsByUserId(Long userId);
    /**
     * 获得练习信息列表
     *
     * @return 脱敏后的用户列表
     */
    List<PracticeRecord> getRecordsList(List<PracticeRecord> practiceRecordList);
    /**
     * 获取查询条件
     * @return
     */
    QueryWrapper<PracticeRecord> getQueryWrapper(PracticeRecordQueryRequest practiceRecordQueryRequest);
}
