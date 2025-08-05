package com.cnj.slrbackend.mapper;

import com.cnj.slrbackend.model.entity.User;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
* @author Administrator
* @description 针对表【user(用户)】的数据库操作Mapper
* @createDate 2025-06-18 19:56:43
* @Entity com.cnj.slrbackend.model.entity.User
*/
@Mapper

public interface UserMapper extends BaseMapper<User> {

}




