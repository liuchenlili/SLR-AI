package com.cnj.slrbackend.service.service.impl;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.collection.CollUtil;
import cn.hutool.core.util.ObjUtil;
import cn.hutool.core.util.StrUtil;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.cnj.slrbackend.exception.BusinessException;
import com.cnj.slrbackend.exception.ErrorCode;
import com.cnj.slrbackend.mapper.PracticeRecordMapper;
import com.cnj.slrbackend.mapper.UserMapper;
import com.cnj.slrbackend.model.dto.predict.PracticeRecordQueryRequest;
import com.cnj.slrbackend.model.dto.user.UserQueryRequest;
import com.cnj.slrbackend.model.entity.PracticeRecord;
import com.cnj.slrbackend.model.entity.User;
import com.cnj.slrbackend.model.enums.UserRoleEnum;
import com.cnj.slrbackend.model.vo.LoginUserVO;
import com.cnj.slrbackend.model.vo.UserVO;
import com.cnj.slrbackend.service.service.PracticeRecordService;
import com.cnj.slrbackend.service.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.util.DigestUtils;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import static com.cnj.slrbackend.constant.UserConstant.USER_LOGIN_STATE;

/**
* @author Administrator
* @description 针对表【user(用户)】的数据库操作Service实现
* @createDate 2025-06-18 19:56:43
*/
@Service
public class PracticeRecordServiceImpl extends ServiceImpl<PracticeRecordMapper, PracticeRecord>
    implements PracticeRecordService {



    /**
     * 保存练习记录
     */
    @Override
    public boolean saveRecord(PracticeRecord record) {
        // 1. 校验参数
        if (record == null || record.getUserId() == null || StrUtil.isBlank(record.getVideoUrl())) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "缺少必要字段");
        }
        // 2. 插入
        return this.save(record); // MyBatis-Plus 自动保存
    }
    /**
     * 查询用户所有练习记录（按创建时间倒序）
     */
    @Override
    public List<PracticeRecord> listRecordsByUserId(Long userId) {
        if (userId == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "用户ID为空");
        }
        QueryWrapper<PracticeRecord> qw = new QueryWrapper<>();
        qw.eq("user_id", userId).orderByDesc("create_time");
        List<PracticeRecord> recordList = this.list(qw);
        return recordList;
    }

    @Override
    public List<PracticeRecord> getRecordsList(List<PracticeRecord> practiceRecordList) {
        if (CollUtil.isEmpty(practiceRecordList)) {
            return new ArrayList<>();
        }
        return practiceRecordList.stream().collect(Collectors.toList());
    }

    @Override
    public QueryWrapper<PracticeRecord> getQueryWrapper(PracticeRecordQueryRequest practiceRecordQueryRequest) {
        if (practiceRecordQueryRequest == null) {
            throw new BusinessException(ErrorCode.PARAMS_ERROR, "请求参数为空");
        }
        Long user_id = practiceRecordQueryRequest.getUser_id();
        String practiceRecordQueryRequestTargetText = practiceRecordQueryRequest.getTarget_text();

        QueryWrapper<PracticeRecord> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq(ObjUtil.isNotNull(user_id), "user_id", user_id);
        queryWrapper.like(StrUtil.isNotBlank(practiceRecordQueryRequestTargetText), "target_text", practiceRecordQueryRequestTargetText);
        return queryWrapper;
    }
}




