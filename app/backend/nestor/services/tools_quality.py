import json
from .tools import tool, _resolve
from .tools_office import _json
from .deliverable_quality import inspect_file


@tool('review_deliverable', 'Mở file Word/Excel/PDF thật để kiểm tra chất lượng trước bàn giao: nội dung rỗng/sơ sài, thiếu phần bắt buộc, lỗi công thức hiển nhiên, chỗ giữ chỗ. required_sections là tên mục/bảng cần có; min_words tùy loại sản phẩm, không dùng số từ để thay kiểm đủ ý. Chỉ bật allow_template khi người dùng thực sự yêu cầu mẫu trống. passed không chứng minh sự chính xác chuyên môn.',
      {'path':('string','Đường dẫn file .docx/.xlsx/.pdf'), 'required_sections':('string','JSON mảng các phần cần có theo yêu cầu đã chốt'), 'min_words':('integer','Ngưỡng nội dung phù hợp sản phẩm, mặc định 20; báo cáo phân tích cần cao hơn'), 'allow_template':('boolean','Cho phép mẫu trống được người dùng yêu cầu rõ')},required=['path'])
def review_deliverable(ctx,path,required_sections='[]',min_words=20,allow_template=False):
    sections=_json(required_sections,'required_sections')
    if not isinstance(sections,list) or any(not isinstance(s,str) for s in sections): raise ValueError('required_sections phải là mảng tên phần')
    if isinstance(min_words,bool) or not isinstance(min_words,int) or min_words<0: raise ValueError('min_words phải là số nguyên không âm')
    return json.dumps(inspect_file(_resolve(ctx,path,'read'),sections,min_words,allow_template),ensure_ascii=False)
