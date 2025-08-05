package com.cnj.slrbackend.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.cnj.slrbackend.model.entity.SignWord;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface SignWordMapper extends BaseMapper<SignWord> {
    @Select("SELECT * FROM sign_word WHERE word LIKE CONCAT('%', #{keyword}, '%') OR chineseMeaning LIKE CONCAT('%', #{keyword}, '%')")
    List<SignWord> searchByKeyword(String keyword);
}





