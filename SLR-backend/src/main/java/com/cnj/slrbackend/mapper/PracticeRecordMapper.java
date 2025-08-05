package com.cnj.slrbackend.mapper;

import com.cnj.slrbackend.model.entity.PracticeRecord;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * @author Administrator
 * @description 针对表【practice_record(练习记录)】的数据库操作Mapper
 * @createDate 2025-07-08
 * @Entity com.cnj.slrbackend.model.entity.PracticeRecord
 */
@Mapper
public interface PracticeRecordMapper extends BaseMapper<PracticeRecord> {

//    @Insert("INSERT INTO practice_record(user_id, video_url, ai_advice, predict_json, target_text, created_at) " +
//            "VALUES (#{userId}, #{videoUrl}, #{aiAdvice}, #{predictJson}, #{targetText}, NOW())")
//    int insert(PracticeRecord record);
//
//    @Select("SELECT * FROM practice_record WHERE user_id=#{userId} ORDER BY created_at DESC")
//    List<PracticeRecord> findByUserId(@Param("userId") Long userId);

}





