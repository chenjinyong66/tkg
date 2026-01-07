import asyncio
import json
import os
import tempfile
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from server.routers.auth_router import get_admin_user
from server.utils.auth_middleware import get_db, get_required_user
from src.plugins.mineru_parser import MinerUParser
from src.plugins.paddlex_parser import PaddleXDocumentParser
from src.plugins.rapid_ocr_processor import RapidOCRProcessor
from src.storage.db.models import User
from src import config as conf
from src.storage.minio.client import get_minio_client, aupload_file_to_minio
from src.knowledge.utils import calculate_content_hash
from src.knowledge.indexing import is_supported_file_extension, SUPPORTED_FILE_EXTENSIONS

talent = APIRouter(prefix="/talent", tags=["talent"])

# 存储人才考核文件信息
talent_files_storage = {}

# 解析器实例
mineru_parser = MinerUParser()
paddlex_parser = PaddleXDocumentParser()
ocr_processor = RapidOCRProcessor()

@talent.get("/talents")
async def get_talents(current_user: User = Depends(get_required_user)):
    """获取人才列表"""
    try:
        # 模拟从数据库获取人才列表
        talents = []
        for file_id, file_info in talent_files_storage.items():
            if file_info.get('user_id') == current_user.id:
                employee_info = file_info.get('employee_info', {})
                # 检查是否已经添加过这个人（通过employeeId去重）
                existing_talent = next((t for t in talents if t['employeeId'] == employee_info.get('employeeId')), None)
                
                if existing_talent:
                    # 如果已存在，更新文件计数
                    existing_talent['fileCount'] += 1
                else:
                    # 添加新人
                    talents.append({
                        'id': file_id,
                        'name': employee_info.get('name', ''),
                        'employeeId': employee_info.get('employeeId', ''),
                        'department': employee_info.get('department', ''),
                        'position': employee_info.get('position', ''),
                        'skills': employee_info.get('skills', []),
                        'contact': employee_info.get('contact', ''),
                        'remarks': employee_info.get('remarks', ''),
                        'createTime': file_info.get('upload_time'),
                        'fileCount': 1
                    })
        
        return {"talents": talents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取人才列表失败: {str(e)}")


@talent.post("/talents")
async def create_talent(
    request_data: dict = Body(...),
    current_user: User = Depends(get_required_user)
):
    """创建人才"""
    try:
        # 生成唯一ID
        talent_id = str(uuid.uuid4())
        
        # 创建人才记录
        talent_record = {
            'filename': f"{request_data.get('name', 'Unknown')}_profile.txt",
            'file_type': 'profile',
            'file_size': 0,
            'upload_time': datetime.now().isoformat(),
            'file_path': '',
            'employee_info': {
                'name': request_data.get('name', ''),
                'employeeId': request_data.get('employeeId', ''),
                'department': request_data.get('department', ''),
                'position': request_data.get('position', ''),
                'skills': request_data.get('skills', []),
                'contact': request_data.get('contact', ''),
                'remarks': request_data.get('remarks', '')
            },
            'user_id': current_user.id,
            'parsed': False,
            'has_graph': False,
            'markdown_content': None,
            'graph_data': None,
            'file_count': 0
        }
        
        # 存储人才信息
        talent_files_storage[talent_id] = talent_record
        
        return {
            "success": True,
            "talent_id": talent_id,
            "message": "人才创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建人才失败: {str(e)}")


@talent.put("/talents/{talent_id}")
async def update_talent(
    talent_id: str,
    request_data: dict = Body(...),
    current_user: User = Depends(get_required_user)
):
    """更新人才信息"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该记录")
        
        # 更新员工信息
        employee_info = file_info.get('employee_info', {})
        for key, value in request_data.items():
            employee_info[key] = value
        file_info['employee_info'] = employee_info
        
        return {
            "success": True,
            "message": "人才信息更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新人才信息失败: {str(e)}")


@talent.delete("/talents/{talent_id}")
async def delete_talent(
    talent_id: str,
    current_user: User = Depends(get_required_user)
):
    """删除人才"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限删除该记录")
        
        # 删除相关的所有文件
        related_files = []
        for fid, f_info in talent_files_storage.items():
            if f_info.get('employee_info', {}).get('employeeId') == file_info.get('employee_info', {}).get('employeeId'):
                related_files.append(fid)
        
        for fid in related_files:
            if os.path.exists(talent_files_storage[fid]['file_path']):
                os.remove(talent_files_storage[fid]['file_path'])
            del talent_files_storage[fid]
        
        return {
            "success": True,
            "message": "人才及关联文件删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除人才失败: {str(e)}")


@talent.get("/talents/{talent_id}")
async def get_talent_detail(
    talent_id: str,
    current_user: User = Depends(get_required_user)
):
    """获取人才详情"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该人才")
        
        # 获取该人才的所有文件
        talent_files = []
        for file_id, info in talent_files_storage.items():
            if (info.get('user_id') == current_user.id and 
                info.get('employee_info', {}).get('employeeId') == file_info.get('employee_info', {}).get('employeeId')):
                talent_files.append({
                    'id': file_id,
                    'filename': info.get('filename'),
                    'fileType': info.get('file_type'),
                    'fileSize': info.get('file_size'),
                    'uploadTime': info.get('upload_time'),
                    'parsed': info.get('parsed', False),
                    'hasGraph': info.get('has_graph', False)
                })
        
        # 返回人才详情
        return {
            "talent": {
                'id': talent_id,
                'name': file_info.get('employee_info', {}).get('name', ''),
                'employeeId': file_info.get('employee_info', {}).get('employeeId', ''),
                'department': file_info.get('employee_info', {}).get('department', ''),
                'position': file_info.get('employee_info', {}).get('position', ''),
                'skills': file_info.get('employee_info', {}).get('skills', []),
                'contact': file_info.get('employee_info', {}).get('contact', ''),
                'remarks': file_info.get('employee_info', {}).get('remarks', ''),
                'createTime': file_info.get('upload_time'),
                'fileCount': len(talent_files)
            },
            "files": talent_files
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取人才详情失败: {str(e)}")


@talent.get("/files")
async def get_talent_files(current_user: User = Depends(get_required_user)):
    """获取考核文件列表（兼容现有接口）"""
    try:
        # 模拟从数据库获取文件列表
        files = []
        for file_id, file_info in talent_files_storage.items():
            if file_info.get('user_id') == current_user.id:
                files.append({
                    'id': file_id,
                    'filename': file_info.get('filename'),
                    'fileType': file_info.get('file_type'),
                    'fileSize': file_info.get('file_size'),
                    'uploadTime': file_info.get('upload_time'),
                    'description': file_info.get('description', ''),
                    'employeeInfo': file_info.get('employee_info', {}),
                    'parsed': file_info.get('parsed', False),
                    'hasGraph': file_info.get('has_graph', False)
                })
        
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取考核文件列表失败: {str(e)}")


@talent.get("/talents/{talent_id}/files")
async def get_talent_files_by_talent(
    talent_id: str,
    current_user: User = Depends(get_required_user)
):
    """获取特定人才的考核文件列表"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该人才")
        
        # 获取该人才的所有文件
        files = []
        for file_id, info in talent_files_storage.items():
            if (info.get('user_id') == current_user.id and 
                info.get('employee_info', {}).get('employeeId') == file_info.get('employee_info', {}).get('employeeId')):
                files.append({
                    'id': file_id,
                    'filename': info.get('filename'),
                    'fileType': info.get('file_type'),
                    'fileSize': info.get('file_size'),
                    'uploadTime': info.get('upload_time'),
                    'parsed': info.get('parsed', False),
                    'hasGraph': info.get('has_graph', False)
                })
        
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取人才文件列表失败: {str(e)}")


@talent.post("/upload")
async def upload_talent_file(
    file: UploadFile = File(...),
    employee_info: str = Form(...),
    current_user: User = Depends(get_required_user)
):
    """上传考核文件"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No selected file")
        
        # 验证文件类型
        if not is_supported_file_extension(file.filename):
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.filename}")
        
        # 验证文件大小（限制为50MB）
        file_content = await file.read()
        if len(file_content) > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=400, detail="文件大小超过50MB限制")
        
        # 验证员工信息
        try:
            employee_info = json.loads(employee_info)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="员工信息格式错误")
        
        # 生成唯一文件ID
        file_id = str(uuid.uuid4())
        
        # 计算文件内容哈希值
        content_hash = await calculate_content_hash(file_content)
        
        # 生成带时间戳的文件名，避免冲突
        import time
        basename, ext = os.path.splitext(file.filename)
        minio_filename = f"{basename}_{int(time.time() * 1000)}{ext}"
        
        # 使用人才专用存储桶
        bucket_name = f"talent-{str(current_user.id).replace('_', '-')}"
        
        # 上传文件到MinIO，使用现有的异步上传函数
        minio_url = await aupload_file_to_minio(bucket_name, minio_filename, file_content, ext.lstrip('.'))
        
        # 存储文件信息
        talent_files_storage[file_id] = {
            'filename': file.filename,
            'file_type': ext[1:] if ext else 'profile',  # 去掉点号，如果没有扩展名则为profile
            'file_size': len(file_content),
            'upload_time': datetime.now().isoformat(),
            'file_path': minio_url,  # MinIO URL路径
            'minio_bucket': bucket_name,
            'minio_filename': minio_filename,
            'employee_info': employee_info,
            'user_id': current_user.id,
            'parsed': False,
            'has_graph': False,
            'markdown_content': None,
            'graph_data': None,
            'file_count': 1,
            'content_hash': content_hash
        }
        
        return {
            "success": True,
            "file_id": file_id,
            "message": "文件上传成功",
            "file_path": minio_url,
            "filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传文件失败: {str(e)}")


@talent.get("/files/{file_id}")
async def get_talent_file_detail(
    file_id: str,
    current_user: User = Depends(get_required_user)
):
    """获取考核文件详情"""
    try:
        if file_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_info = talent_files_storage[file_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该文件")
        
        return {
            "file": {
                'id': file_id,
                'filename': file_info.get('filename'),
                'fileType': file_info.get('file_type'),
                'fileSize': file_info.get('file_size'),
                'uploadTime': file_info.get('upload_time'),
                'employeeInfo': file_info.get('employee_info'),
                'parsed': file_info.get('parsed', False),
                'hasGraph': file_info.get('has_graph', False)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件详情失败: {str(e)}")


@talent.put("/files/{file_id}/employee")
async def update_employee_info(
    file_id: str,
    request_data: dict = Body(...),
    current_user: User = Depends(get_required_user)
):
    """更新员工信息"""
    try:
        if file_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[file_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该记录")
        
        # 更新员工信息
        employee_info = file_info.get('employee_info', {})
        employee_info.update(request_data)
        file_info['employee_info'] = employee_info
        
        return {
            "success": True,
            "message": "员工信息更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新员工信息失败: {str(e)}")


@talent.delete("/files/{file_id}")
async def delete_talent_file(
    file_id: str,
    current_user: User = Depends(get_required_user)
):
    """删除人才记录（文件）"""
    try:
        if file_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_info = talent_files_storage[file_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限删除该文件")
        
        # 从MinIO删除文件
        minio_client = get_minio_client()
        bucket_name = file_info.get('minio_bucket')
        minio_filename = file_info.get('minio_filename')
        
        if minio_filename and bucket_name:
            try:
                await minio_client.adelete_file(bucket_name, minio_filename)
            except Exception as e:
                print(f"删除MinIO文件失败: {e}")
        
        # 从存储中删除记录
        del talent_files_storage[file_id]
        
        return {
            "success": True,
            "message": "文件删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")


@talent.post("/files/{file_id}/parse")
async def parse_file_to_markdown(
    file_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_required_user)
):
    """解析文件为Markdown"""
    try:
        if file_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_info = talent_files_storage[file_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该文件")
        
        # 从MinIO下载文件
        bucket_name = file_info.get('minio_bucket')
        minio_filename = file_info.get('minio_filename')
        
        if not minio_filename or not bucket_name:
            raise HTTPException(status_code=404, detail="文件在MinIO中不存在")
        
        # 下载文件内容
        try:
            minio_client = get_minio_client()
            file_content = await minio_client.adownload_file(bucket_name, minio_filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")
        
        # 根据文件类型决定是否需要解析
        file_ext = os.path.splitext(file_info.get('filename', ''))[1].lower()
        markdown_content = ""
        
        # 对于纯文本文件，直接解码内容
        if file_ext in ['.txt', '.md']:
            try:
                markdown_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                # 如果UTF-8解码失败，尝试其他编码
                try:
                    markdown_content = file_content.decode('gbk')
                except UnicodeDecodeError:
                    markdown_content = file_content.decode('utf-8', errors='ignore')
        else:
            # 对于其他文件类型，使用解析器
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                if file_ext in ['.pdf', '.doc', '.docx']:
                    # 使用MinerU解析器
                    try:
                        markdown_content = await mineru_parser.parse_to_markdown(temp_file_path)
                    except Exception as e:
                        print(f"MinerU解析失败: {e}")
                        # 尝试其他解析器
                        if file_ext == '.pdf':
                            # 使用OCR解析PDF
                            markdown_content = await ocr_processor.process_pdf(temp_file_path)
                        elif file_ext in ['.doc', '.docx']:
                            # 使用pandas或其他方式处理文档
                            with open(temp_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                markdown_content = f.read()
                        else:
                            with open(temp_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                markdown_content = f.read()
                elif file_ext in ['.xls', '.xlsx']:
                    # 使用pandas解析Excel
                    df = pd.read_excel(temp_file_path)
                    markdown_content = df.to_markdown()
                else:
                    # 默认处理
                    with open(temp_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        markdown_content = f.read()
            finally:
                # 清理临时文件
                os.unlink(temp_file_path)
        
        # 保存解析结果
        file_info['parsed'] = True
        file_info['markdown_content'] = markdown_content
        
        return {
            "success": True,
            "content": markdown_content,
            "message": "文件解析成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析文件失败: {str(e)}")


@talent.get("/files/{file_id}/markdown")
async def get_markdown_content(
    file_id: str,
    current_user: User = Depends(get_required_user)
):
    """获取解析后的Markdown内容"""
    try:
        if file_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_info = talent_files_storage[file_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该文件")
        
        markdown_content = file_info.get('markdown_content')
        if not markdown_content:
            raise HTTPException(status_code=404, detail="文件尚未解析或无内容")
        
        return {
            "content": markdown_content
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Markdown内容失败: {str(e)}")


@talent.put("/files/{file_id}/markdown")
async def update_markdown_content(
    file_id: str,
    request_data: dict = Body(...),
    current_user: User = Depends(get_required_user)
):
    """更新Markdown内容"""
    try:
        if file_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_info = talent_files_storage[file_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该文件")
        
        content = request_data.get('content')
        if not content:
            raise HTTPException(status_code=400, detail="内容不能为空")
        
        file_info['markdown_content'] = content
        
        return {
            "success": True,
            "message": "内容更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新内容失败: {str(e)}")


@talent.post("/files/{file_id}/extract-graph")
async def extract_knowledge_graph(
    file_id: str,
    current_user: User = Depends(get_required_user)
):
    """从Markdown内容抽取知识图谱"""
    try:
        if file_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_info = talent_files_storage[file_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该文件")
        
        markdown_content = file_info.get('markdown_content')
        if not markdown_content:
            raise HTTPException(status_code=400, detail="文件尚未解析或无内容")
        
        # 模拟知识图谱抽取 - 实际应用中应调用大模型API
        # 这里我们创建一个示例图谱结构
        # 在实际应用中，这里应该调用大模型API进行实体和关系抽取
        import re
        
        # 简单的实体抽取示例（实际应用中应使用更复杂的NLP模型）
        entities = []
        relationships = []
        
        # 提取员工相关信息作为实体
        employee_info = file_info.get('employee_info', {})
        if employee_info.get('name'):
            entities.append({
                "id": f"emp_{employee_info['name']}",
                "label": employee_info['name'],
                "type": "Employee",
                "properties": {
                    "name": employee_info['name'],
                    "department": employee_info.get('department', ''),
                    "employeeId": employee_info.get('employeeId', '')
                }
            })
        
        # 提取技能和考核指标作为实体
        skills = re.findall(r'技能[:：]\s*([^\n\r,，]+)', markdown_content)
        for skill in skills:
            entities.append({
                "id": f"skill_{skill.strip()}",
                "label": skill.strip(),
                "type": "Skill",
                "properties": {"name": skill.strip()}
            })
        
        # 提取绩效指标作为实体
        metrics = re.findall(r'(?:绩效|考核|指标)[:：]\s*([^\n\r,，]+)', markdown_content)
        for metric in metrics:
            entities.append({
                "id": f"metric_{metric.strip()}",
                "label": metric.strip(),
                "type": "PerformanceMetric",
                "properties": {"name": metric.strip()}
            })
        
        # 创建关系
        for entity in entities:
            if entity['type'] == 'Employee':
                for skill_entity in entities:
                    if skill_entity['type'] == 'Skill':
                        relationships.append({
                            "source": entity['id'],
                            "target": skill_entity['id'],
                            "type": "HAS_SKILL",
                            "properties": {"level": "unknown"}
                        })
        
        graph_data = {
            "nodes": entities,
            "edges": relationships
        }
        
        # 保存图谱数据
        file_info['has_graph'] = True
        file_info['graph_data'] = graph_data
        
        return {
            "success": True,
            "graphData": graph_data,
            "message": "知识图谱抽取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"抽取知识图谱失败: {str(e)}")


@talent.get("/files/{file_id}/graph")
async def get_knowledge_graph(
    file_id: str,
    current_user: User = Depends(get_required_user)
):
    """获取知识图谱数据"""
    try:
        if file_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_info = talent_files_storage[file_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该文件")
        
        graph_data = file_info.get('graph_data')
        if not graph_data:
            raise HTTPException(status_code=404, detail="知识图谱尚未生成")
        
        return {
            "graphData": graph_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取知识图谱失败: {str(e)}")


@talent.get("/employee/{employee_id}/review")
async def get_employee_review(
    employee_id: str,
    current_user: User = Depends(get_required_user)
):
    """获取员工考核信息"""
    try:
        # 模拟获取员工考核信息
        # 在实际应用中，这里应该从数据库中查询
        employee_reviews = []
        for file_id, file_info in talent_files_storage.items():
            if (file_info.get('user_id') == current_user.id and 
                file_info.get('employee_info', {}).get('employeeId') == employee_id):
                employee_reviews.append({
                    'fileId': file_id,
                    'filename': file_info.get('filename'),
                    'reviewPeriod': file_info.get('employee_info', {}).get('reviewPeriod'),
                    'uploadTime': file_info.get('upload_time'),
                    'parsed': file_info.get('parsed', False)
                })
        
        return {
            "employeeId": employee_id,
            "reviews": employee_reviews
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取员工考核信息失败: {str(e)}")


@talent.get("/files/{file_id}/content")
async def get_file_content(
    file_id: str,
    current_user: User = Depends(get_required_user)
):
    """直接获取文件内容（适用于文本文件）"""
    try:
        if file_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_info = talent_files_storage[file_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该文件")
        
        # 从MinIO下载文件
        bucket_name = file_info.get('minio_bucket')
        minio_filename = file_info.get('minio_filename')
        
        if not minio_filename or not bucket_name:
            raise HTTPException(status_code=404, detail="文件在MinIO中不存在")
        
        # 下载文件内容
        try:
            minio_client = get_minio_client()
            file_content = await minio_client.adownload_file(bucket_name, minio_filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")
        
        # 根据文件类型决定如何返回内容
        file_ext = os.path.splitext(file_info.get('filename', ''))[1].lower()
        
        if file_ext in ['.txt', '.md']:
            try:
                content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                # 如果UTF-8解码失败，尝试其他编码
                try:
                    content = file_content.decode('gbk')
                except UnicodeDecodeError:
                    content = file_content.decode('utf-8', errors='ignore')
            
            # 保存到存储中，标记为已解析
            file_info['parsed'] = True
            file_info['markdown_content'] = content
            
            return {
                "content": content,
                "success": True
            }
        else:
            raise HTTPException(status_code=400, detail="此接口仅支持文本文件(.txt, .md)")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件内容失败: {str(e)}")


@talent.get("/files/{file_id}/export")
async def export_review_report(
    file_id: str,
    current_user: User = Depends(get_required_user)
):
    """导出考核报告"""
    try:
        if file_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        file_info = talent_files_storage[file_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该文件")
        
        # 这里我们返回一个模拟的PDF报告
        # 在实际应用中，这里应该生成真正的PDF报告
        from io import BytesIO
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, f"人才考核报告 - {file_info.get('filename')}")
        c.drawString(100, 730, f"员工: {file_info.get('employee_info', {}).get('name', '未知')}")
        c.drawString(100, 710, f"部门: {file_info.get('employee_info', {}).get('department', '未知')}")
        c.drawString(100, 690, f"考核周期: {file_info.get('employee_info', {}).get('reviewPeriod', '未知')}")
        
        # 添加一些其他信息
        markdown_content = file_info.get('markdown_content', '')
        if markdown_content:
            # 限制内容长度以适应PDF
            content_preview = markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content
            c.drawString(100, 670, "内容摘要:")
            textobject = c.beginText(100, 650)
            for line in content_preview.split('\n')[:10]:  # 只显示前10行
                textobject.textLine(line[:80])  # 每行最多80字符
            c.drawText(textobject)
        
        c.save()
        buffer.seek(0)
        
        # 返回PDF内容
        return buffer.getvalue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出报告失败: {str(e)}")


@talent.get("/stats")
async def get_talent_stats(
    current_user: User = Depends(get_required_user)
):
    """获取人才统计信息"""
    try:
        # 统计用户的所有人才和文件
        user_files = [file_info for file_info in talent_files_storage.values() 
                     if file_info.get('user_id') == current_user.id]
        
        # 统计解析的文件数量
        parsed_files = len([f for f in user_files if f.get('parsed', False)])
        
        # 统计有图谱的文件数量
        graph_extracted = len([f for f in user_files if f.get('has_graph', False)])
        
        # 计算平均评分（如果有的话）
        ratings = [f.get('employee_info', {}).get('rating', 0) for f in user_files 
                  if f.get('employee_info', {}).get('rating') is not None]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # 计算人才总数（根据员工ID去重）
        employee_ids = set()
        for file_info in user_files:
            emp_id = file_info.get('employee_info', {}).get('employeeId')
            if emp_id:
                employee_ids.add(emp_id)
        total_talents = len(employee_ids)
        
        stats_data = {
            "totalTalents": total_talents,
            "parsedFiles": parsed_files,
            "graphExtracted": graph_extracted,
            "averageRating": round(average_rating, 2) if ratings else 0,
            "totalFiles": len(user_files)
        }
        
        return {
            "stats": stats_data,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@talent.get("/talents/{talent_id}/overall-rating")
async def get_talent_overall_rating(
    talent_id: str,
    current_user: User = Depends(get_required_user)
):
    """获取人才综合评分"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该人才")
        
        # 计算综合评分（这里使用模拟数据，实际应用中应该根据具体算法计算）
        employee_info = file_info.get('employee_info', {})
        
        # 模拟评分计算
        rating_data = {
            "score": employee_info.get('rating', 7.5),  # 使用现有评分或默认值
            "technical": employee_info.get('technical_rating', 7.0),
            "management": employee_info.get('management_rating', 7.0),
            "communication": employee_info.get('communication_rating', 7.0),
            "innovation": employee_info.get('innovation_rating', 7.0),
            "execution": employee_info.get('execution_rating', 7.0),
            "teamwork": employee_info.get('teamwork_rating', 7.0)
        }
        
        return {
            "rating": rating_data,
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取综合评分失败: {str(e)}")


@talent.get("/talents/{talent_id}/team-comparison")
async def get_team_comparison(
    talent_id: str,
    time_range: str = "quarter",
    current_user: User = Depends(get_required_user)
):
    """获取团队对比数据"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该人才")
        
        # 模拟团队对比数据（实际应用中应从数据库获取团队数据）
        team_avg_data = {
            "technical": 7.2,
            "management": 6.8,
            "communication": 7.5,
            "innovation": 6.9,
            "execution": 7.1,
            "teamwork": 7.3
        }
        
        return {
            "data": team_avg_data,
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取团队对比数据失败: {str(e)}")


@talent.get("/talents/{talent_id}/trend")
async def get_talent_trend(
    talent_id: str,
    current_user: User = Depends(get_required_user),
    dimension: str = "technical",
    time_range: str = "quarter",
    compare_mode: str = "none"
):
    """获取人才趋势数据"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该人才")
        
        # 模拟趋势数据（实际应用中应从历史数据中获取）
        import random
        from datetime import datetime, timedelta
        
        # 生成模拟的时间序列数据
        trend_data = []
        now = datetime.now()
        
        # 根据时间范围生成数据点
        if time_range == "month":
            days = 30
        elif time_range == "quarter":
            days = 90
        elif time_range == "halfYear":
            days = 180
        elif time_range == "year":
            days = 365
        else:
            days = 30  # 默认一个月
        
        # 每隔几天生成一个数据点
        step = max(1, days // 10)
        for i in range(0, days + 1, step):
            date = now - timedelta(days=days - i)
            score = 6.0 + random.random() * 3.0  # 6.0-9.0之间的随机分数
            
            point = {
                "time": date.isoformat(),
                "score": round(score, 1),
                "type": "当前人才"
            }
            trend_data.append(point)
            
            # 如果需要对比团队数据
            if compare_mode == "team":
                team_score = 6.0 + random.random() * 2.0  # 团队平均分
                team_point = {
                    "time": date.isoformat(),
                    "score": round(team_score, 1),
                    "type": "团队平均"
                }
                trend_data.append(team_point)
        
        return {
            "data": trend_data,
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")


@talent.get("/talents/{talent_id}/analysis")
async def get_talent_analysis(
    talent_id: str,
    time_range: str = "quarter",
    current_user: User = Depends(get_required_user)
):
    """获取人才详细分析"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该人才")
        
        # 模拟详细分析数据
        analysis_data = [
            {
                "id": "1",
                "dimension": "技术能力",
                "dimensionKey": "technical",
                "score": 8.2,
                "level": "good",
                "trend": "up",
                "trendValue": 0.5,
                "evaluateTime": (datetime.now() - timedelta(days=10)).isoformat(),
                "evaluator": "上级领导",
                "description": "专业技术扎实，具备解决复杂技术问题的能力"
            },
            {
                "id": "2",
                "dimension": "管理能力",
                "dimensionKey": "management",
                "score": 7.0,
                "level": "average",
                "trend": "stable",
                "trendValue": 0.0,
                "evaluateTime": (datetime.now() - timedelta(days=10)).isoformat(),
                "evaluator": "上级领导",
                "description": "项目管理能力良好，有待进一步提升"
            },
            {
                "id": "3",
                "dimension": "沟通能力",
                "dimensionKey": "communication",
                "score": 8.5,
                "level": "good",
                "trend": "up",
                "trendValue": 0.8,
                "evaluateTime": (datetime.now() - timedelta(days=10)).isoformat(),
                "evaluator": "上级领导",
                "description": "沟通表达能力优秀，团队协作良好"
            },
            {
                "id": "4",
                "dimension": "创新能力",
                "dimensionKey": "innovation",
                "score": 7.8,
                "level": "good",
                "trend": "down",
                "trendValue": -0.3,
                "evaluateTime": (datetime.now() - timedelta(days=10)).isoformat(),
                "evaluator": "上级领导",
                "description": "具备创新思维，能提出有效解决方案"
            }
        ]
        
        return {
            "analysis": analysis_data,
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取详细分析失败: {str(e)}")


@talent.get("/talents/{talent_id}/suggestions")
async def get_talent_suggestions(
    talent_id: str,
    current_user: User = Depends(get_required_user)
):
    """获取人才改进建议"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该人才")
        
        # 模拟改进建议数据
        suggestions_data = [
            {
                "id": "1",
                "content": "加强新技术学习，关注行业前沿发展",
                "dimension": "technical",
                "priority": "high",
                "createTime": (datetime.now() - timedelta(days=15)).isoformat(),
                "status": "pending"
            },
            {
                "id": "2",
                "content": "提升团队管理技能，学习先进管理理念",
                "dimension": "management",
                "priority": "medium",
                "createTime": (datetime.now() - timedelta(days=12)).isoformat(),
                "status": "pending"
            },
            {
                "id": "3",
                "content": "参加沟通技巧培训，提高跨部门协作效率",
                "dimension": "communication",
                "priority": "low",
                "createTime": (datetime.now() - timedelta(days=10)).isoformat(),
                "status": "pending"
            }
        ]
        
        return {
            "suggestions": suggestions_data,
            "success": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取改进建议失败: {str(e)}")


@talent.get("/talents/{talent_id}/analysis/report")
async def export_talent_analysis_report(
    talent_id: str,
    current_user: User = Depends(get_required_user),
    time_range: str = "quarter",
    include_charts: bool = True,
    include_suggestions: bool = True
):
    """导出人才分析报告"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该人才")
        
        # 这里我们返回一个模拟的PDF报告
        from io import BytesIO
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, f"人才能力分析报告 - {file_info.get('employee_info', {}).get('name', '未知')}")
        c.drawString(100, 730, f"员工ID: {file_info.get('employee_info', {}).get('employeeId', '未知')}")
        c.drawString(100, 710, f"部门: {file_info.get('employee_info', {}).get('department', '未知')}")
        
        # 添加综合评分
        c.drawString(100, 690, "综合评分:")
        c.drawString(120, 670, f"总分: {file_info.get('employee_info', {}).get('rating', 7.5)}/10.0")
        
        # 添加能力详情
        c.drawString(100, 650, "能力详情:")
        c.drawString(120, 630, "- 技术能力: 8.2/10.0")
        c.drawString(120, 610, "- 管理能力: 7.0/10.0")
        c.drawString(120, 590, "- 沟通能力: 8.5/10.0")
        c.drawString(120, 570, "- 创新能力: 7.8/10.0")
        
        # 添加改进建议
        c.drawString(100, 540, "改进建议:")
        c.drawString(120, 520, "1. 加强新技术学习，关注行业前沿发展")
        c.drawString(120, 500, "2. 提升团队管理技能，学习先进管理理念")
        c.drawString(120, 480, "3. 参加沟通技巧培训，提高跨部门协作效率")
        
        c.save()
        buffer.seek(0)
        
        # 返回PDF内容
        return buffer.getvalue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出分析报告失败: {str(e)}")


@talent.post("/talents/{talent_id}/assessment")
async def submit_talent_assessment(
    talent_id: str,
    request_data: dict = Body(...),
    current_user: User = Depends(get_required_user)
):
    """提交人才评估"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该人才")
        
        # 更新员工信息中的评分
        employee_info = file_info.get('employee_info', {})
        scores = request_data.get('scores', [])
        
        # 计算平均分
        if scores:
            total_score = sum([score.get('score', 0) for score in scores])
            avg_score = total_score / len(scores) if len(scores) > 0 else 0
            employee_info['rating'] = avg_score
        
        # 保存评估数据（这里简单地将评估数据存储在文件信息中）
        if 'assessments' not in file_info:
            file_info['assessments'] = []
        
        assessment_data = {
            'id': str(uuid.uuid4()),
            'talent_id': talent_id,
            'scores': scores,
            'averageScore': request_data.get('averageScore', 0),
            'remarks': request_data.get('remarks', ''),
            'timeRange': request_data.get('timeRange', 'quarter'),
            'type': request_data.get('type', 'general'),
            'createTime': datetime.now().isoformat(),
            'evaluator': current_user.username
        }
        
        file_info['assessments'].append(assessment_data)
        file_info['employee_info'] = employee_info
        
        return {
            "success": True,
            "message": "评估提交成功",
            "assessment_id": assessment_data['id']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交评估失败: {str(e)}")


@talent.delete("/assessments/{assessment_id}")
async def delete_assessment(
    assessment_id: str,
    current_user: User = Depends(get_required_user)
):
    """删除评估"""
    try:
        # 查找评估所属的人才记录
        talent_record = None
        talent_key = None
        for key, file_info in talent_files_storage.items():
            if file_info.get('user_id') == current_user.id:
                assessments = file_info.get('assessments', [])
                for assessment in assessments:
                    if assessment.get('id') == assessment_id:
                        talent_record = file_info
                        talent_key = key
                        break
            if talent_record:
                break
        
        if not talent_record:
            raise HTTPException(status_code=404, detail="评估记录不存在")
        
        # 从评估列表中移除
        assessments = talent_record.get('assessments', [])
        assessments = [a for a in assessments if a.get('id') != assessment_id]
        talent_record['assessments'] = assessments
        
        return {
            "success": True,
            "message": "评估删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除评估失败: {str(e)}")


@talent.put("/assessments/{assessment_id}")
async def update_assessment(
    assessment_id: str,
    request_data: dict = Body(...),
    current_user: User = Depends(get_required_user)
):
    """更新评估"""
    try:
        # 查找评估所属的人才记录
        talent_record = None
        talent_key = None
        for key, file_info in talent_files_storage.items():
            if file_info.get('user_id') == current_user.id:
                assessments = file_info.get('assessments', [])
                for i, assessment in enumerate(assessments):
                    if assessment.get('id') == assessment_id:
                        talent_record = file_info
                        talent_key = key
                        # 更新评估数据
                        assessments[i].update(request_data)
                        break
            if talent_record:
                break
        
        if not talent_record:
            raise HTTPException(status_code=404, detail="评估记录不存在")
        
        return {
            "success": True,
            "message": "评估更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新评估失败: {str(e)}")


@talent.post("/talents/{talent_id}/assessments")
async def add_assessment(
    talent_id: str,
    request_data: dict = Body(...),
    current_user: User = Depends(get_required_user)
):
    """添加评估"""
    try:
        if talent_id not in talent_files_storage:
            raise HTTPException(status_code=404, detail="人才记录不存在")
        
        file_info = talent_files_storage[talent_id]
        if file_info.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="无权限访问该人才")
        
        # 创建新的评估记录
        assessment_data = {
            'id': str(uuid.uuid4()),
            'talent_id': talent_id,
            'dimension': request_data.get('dimension', ''),
            'score': request_data.get('score', 0),
            'remarks': request_data.get('remarks', ''),
            'evaluator': request_data.get('evaluator', current_user.username),
            'createTime': datetime.now().isoformat()
        }
        
        # 添加到人才记录中
        if 'assessments' not in file_info:
            file_info['assessments'] = []
        
        file_info['assessments'].append(assessment_data)
        
        # 更新员工信息中的评分
        employee_info = file_info.get('employee_info', {})
        if 'rating' not in employee_info:
            employee_info['rating'] = assessment_data['score']
        else:
            # 计算平均分
            assessments = file_info.get('assessments', [])
            total_score = sum([a.get('score', 0) for a in assessments])
            avg_score = total_score / len(assessments) if len(assessments) > 0 else assessment_data['score']
            employee_info['rating'] = avg_score
        
        file_info['employee_info'] = employee_info
        
        return {
            "success": True,
            "message": "评估添加成功",
            "assessment_id": assessment_data['id']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加评估失败: {str(e)}")


@talent.post("/suggestions/{suggestion_id}/done")
async def mark_suggestion_done(
    suggestion_id: str,
    current_user: User = Depends(get_required_user)
):
    """标记建议为完成"""
    try:
        # 在当前实现中，我们没有存储建议的详细信息
        # 这里只是返回成功状态，实际应用中需要更新数据库
        return {
            "success": True,
            "message": "建议状态已更新"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新建议状态失败: {str(e)}")
