import { SAMPLE_CV, SAMPLE_PHOTO, type CvData } from './types';

/** Industries a template is meant for; each has its own sample CV so the gallery shows realistic content. */
export const CV_FIELDS = [
  { id: 'cntt', label: 'Công nghệ thông tin' },
  { id: 'thietke', label: 'Thiết kế & sáng tạo' },
  { id: 'marketing', label: 'Marketing & bán hàng' },
  { id: 'taichinh', label: 'Kế toán & tài chính' },
  { id: 'nhansu', label: 'Nhân sự & hành chính' },
  { id: 'yte', label: 'Y tế & giáo dục' },
  { id: 'kythuat', label: 'Kỹ thuật & sản xuất' },
  { id: 'quanly', label: 'Quản lý & điều hành' },
  { id: 'dichvu', label: 'Dịch vụ & du lịch' },
  { id: 'sinhvien', label: 'Sinh viên, mới ra trường' },
] as const;
export type CvFieldId = (typeof CV_FIELDS)[number]['id'];

export const b = (name: string, title: string, summary: string, rest: Partial<CvData>): CvData => ({
  name, title, summary, email: 'lienhe@email.com', phone: '0912 345 678', address: 'Hà Nội', website: '', photo: SAMPLE_PHOTO,
  experience: [], education: [], skills: [], languages: [{ id: 'l1', name: 'Tiếng Anh', level: 'Giao tiếp tốt' }], projects: [], awards: '', highlights: [], interests: '', ...rest,
});
export const e = (id: string, role: string, company: string, from: string, to: string, desc: string) => ({ id, role, company, from, to, desc });
export const sk = (...a: [string, number][]) => a.map(([name, level], i) => ({ id: `s${i}`, name, level }));

export const FIELD_SAMPLES: Record<CvFieldId, CvData> = {
  cntt: SAMPLE_CV,
  thietke: b('Hoàng Tú Quỳnh', 'Graphic Designer', 'Hơn 5 năm thiết kế nhận diện thương hiệu, ấn phẩm và giao diện số. Thích kể chuyện bằng hình ảnh, làm việc nhóm tốt và luôn giữ đúng deadline.', {
    address: 'Quận 3, TP. Hồ Chí Minh', website: 'behance.net/tuquynh',
    experience: [e('e1', 'Senior Graphic Designer', 'Agency Hoa Sen', '2021', 'Hiện tại', 'Dẫn dắt thiết kế nhận diện cho hơn 30 thương hiệu F&B và thời trang.\nXây dựng bộ quy chuẩn thiết kế giúp rút ngắn 40% thời gian bàn giao.'), e('e2', 'Graphic Designer', 'Studio Mây', '2018', '2021', 'Thiết kế poster, banner, bao bì và bộ ảnh sản phẩm cho khách hàng trong nước.')],
    education: [{ id: 'd1', school: 'Đại học Mỹ thuật Công nghiệp', degree: 'Thiết kế đồ hoạ', from: '2014', to: '2018', desc: '' }],
    skills: sk(['Photoshop', 5], ['Illustrator', 5], ['Figma', 4], ['After Effects', 3], ['Typography', 5]),
    projects: [{ id: 'p1', name: 'Rebrand chuỗi cà phê Nắng', desc: 'Tăng 25% lượng khách quen sau 6 tháng ra mắt.' }], awards: 'Giải Bạc Vietnam Design Awards 2023', highlights: [{ id: 'h1', value: '5+', label: 'năm thiết kế' }, { id: 'h2', value: '30+', label: 'thương hiệu' }, { id: 'h3', value: '-40%', label: 'thời gian bàn giao' }], interests: 'Vẽ minh hoạ\nNhiếp ảnh phố\nGốm thủ công', }),
  marketing: b('Phạm Mỹ Linh', 'Chuyên viên Marketing', '4 năm kinh nghiệm digital marketing cho ngành bán lẻ và thương mại điện tử. Giỏi phân tích số liệu, tối ưu chi phí quảng cáo và xây dựng nội dung chuyển đổi.', {
    address: 'Cầu Giấy, Hà Nội', website: 'linkedin.com/in/mylinh',
    experience: [e('e1', 'Digital Marketing Executive', 'Công ty Cổ phần An Phát', '2022', 'Hiện tại', 'Quản lý ngân sách quảng cáo 300 triệu/tháng trên Meta và Google.\nTăng doanh thu online 62% trong 12 tháng, giảm 20% chi phí mỗi đơn.\nPhối hợp đội nội dung và thiết kế triển khai 15 chiến dịch.'), e('e2', 'Content Marketer', 'Công ty TNHH Mộc Lan', '2020', '2022', 'Viết bài SEO, kịch bản video ngắn, tăng 3 lần lượng truy cập tự nhiên.')],
    education: [{ id: 'd1', school: 'Đại học Kinh tế Quốc dân', degree: 'Marketing', from: '2016', to: '2020', desc: '' }],
    skills: sk(['Facebook Ads', 5], ['Google Analytics', 4], ['SEO', 4], ['Content', 5], ['Canva', 4]), awards: 'Nhân viên xuất sắc quý 3/2023', highlights: [{ id: 'h1', value: '+62%', label: 'doanh thu online' }, { id: 'h2', value: '-20%', label: 'chi phí mỗi đơn' }, { id: 'h3', value: '15', label: 'chiến dịch' }, { id: 'h4', value: '300tr', label: 'ngân sách/tháng' }], interests: 'Đọc sách kinh doanh\nDu lịch\nYoga', }),
  taichinh: b('Lê Ngọc Bích', 'Kế toán tổng hợp', '6 năm kinh nghiệm kế toán tổng hợp, lập báo cáo tài chính và kê khai thuế cho doanh nghiệp sản xuất. Cẩn thận, trung thực, thành thạo các phần mềm kế toán.', {
    address: 'Quận Hải Châu, Đà Nẵng',
    experience: [e('e1', 'Kế toán tổng hợp', 'Công ty CP Thiết bị Nam Việt', '2019', 'Hiện tại', 'Lập báo cáo tài chính, báo cáo thuế hằng tháng, quý, năm.\nĐối chiếu công nợ, kiểm soát chi phí, giảm sai lệch sổ sách xuống dưới 1%.\nLàm việc với kiểm toán độc lập và cơ quan thuế.'), e('e2', 'Kế toán viên', 'Công ty TNHH Hải Đăng', '2017', '2019', 'Hạch toán thu chi, theo dõi tài sản cố định và lương.')],
    education: [{ id: 'd1', school: 'Đại học Kinh tế Đà Nẵng', degree: 'Kế toán doanh nghiệp', from: '2013', to: '2017', desc: 'Tốt nghiệp loại Giỏi' }],
    skills: sk(['MISA', 5], ['Excel nâng cao', 5], ['Báo cáo thuế', 5], ['Kế toán quản trị', 4]), awards: 'Chứng chỉ Kế toán trưởng\nChứng chỉ ACCA F1-F3', highlights: [{ id: 'h1', value: '6', label: 'năm kinh nghiệm' }, { id: 'h2', value: '<1%', label: 'sai lệch sổ sách' }, { id: 'h3', value: '2', label: 'chứng chỉ quốc tế' }], interests: 'Đọc sách tài chính\nCầu lông', }),
  nhansu: b('Nguyễn Thu Lan', 'Chuyên viên Nhân sự', '5 năm làm tuyển dụng và hành chính nhân sự. Giao tiếp tốt, xây dựng quy trình onboarding và văn hoá doanh nghiệp, am hiểu luật lao động.', {
    address: 'Quận 7, TP. Hồ Chí Minh',
    experience: [e('e1', 'HR Executive', 'Tập đoàn Sao Mai', '2021', 'Hiện tại', 'Tuyển dụng hơn 120 nhân sự mỗi năm cho khối văn phòng và kinh doanh.\nXây dựng quy trình onboarding, giảm 30% nhân viên nghỉ trong 3 tháng đầu.\nQuản lý hồ sơ, bảo hiểm và hợp đồng lao động.'), e('e2', 'Chuyên viên tuyển dụng', 'Công ty Thành Công', '2019', '2021', 'Đăng tin, sàng lọc hồ sơ, phỏng vấn và đàm phán offer.')],
    education: [{ id: 'd1', school: 'Đại học Lao động - Xã hội', degree: 'Quản trị nhân lực', from: '2015', to: '2019', desc: '' }],
    skills: sk(['Tuyển dụng', 5], ['Luật lao động', 4], ['C&B', 4], ['Đào tạo', 4], ['Excel', 4]), highlights: [{ id: 'h1', value: '120+', label: 'nhân sự tuyển/năm' }, { id: 'h2', value: '-30%', label: 'nghỉ việc 3 tháng đầu' }, { id: 'h3', value: '5', label: 'năm kinh nghiệm' }], interests: 'Tổ chức sự kiện\nTình nguyện\nNấu ăn', }),
  yte: b('Trần Thị Hạnh', 'Điều dưỡng viên', 'Điều dưỡng 5 năm tại khoa Nội tổng hợp, tận tâm, chịu được áp lực và có kỹ năng chăm sóc bệnh nhân toàn diện. Mong muốn làm việc tại cơ sở y tế chất lượng cao.', {
    address: 'Quận Ninh Kiều, Cần Thơ',
    experience: [e('e1', 'Điều dưỡng khoa Nội', 'Bệnh viện Đa khoa Cần Thơ', '2020', 'Hiện tại', 'Chăm sóc, theo dõi 15-20 bệnh nhân mỗi ca, thực hiện y lệnh chính xác.\nHướng dẫn điều dưỡng mới và sinh viên thực tập.\nTham gia cấp cứu và hồi sức theo phác đồ.'), e('e2', 'Điều dưỡng viên', 'Phòng khám Tâm An', '2018', '2020', 'Tiếp đón, tiêm truyền, lấy mẫu xét nghiệm.')],
    education: [{ id: 'd1', school: 'Đại học Y Dược Cần Thơ', degree: 'Cử nhân Điều dưỡng', from: '2014', to: '2018', desc: '' }],
    skills: sk(['Chăm sóc bệnh nhân', 5], ['Sơ cấp cứu', 5], ['Hồ sơ bệnh án', 4], ['Giao tiếp', 5]), awards: 'Chứng chỉ hành nghề điều dưỡng\nChứng chỉ BLS', highlights: [{ id: 'h1', value: '5', label: 'năm lâm sàng' }, { id: 'h2', value: '15-20', label: 'bệnh nhân/ca' }, { id: 'h3', value: '2', label: 'chứng chỉ hành nghề' }], interests: 'Tình nguyện y tế\nĐọc sách\nĐi bộ', }),
  kythuat: b('Vũ Đức Minh', 'Kỹ sư cơ khí', 'Kỹ sư cơ khí 5 năm kinh nghiệm thiết kế và cải tiến dây chuyền sản xuất, thành thạo CAD/CAM, định hướng tối ưu chi phí và an toàn lao động.', {
    address: 'Biên Hoà, Đồng Nai',
    experience: [e('e1', 'Kỹ sư thiết kế', 'Công ty Cơ khí Đại Phát', '2021', 'Hiện tại', 'Thiết kế chi tiết máy và đồ gá bằng SolidWorks, AutoCAD.\nCải tiến quy trình gia công, tăng 18% năng suất và giảm 12% phế phẩm.\nGiám sát lắp đặt, nghiệm thu thiết bị tại nhà máy khách hàng.'), e('e2', 'Kỹ sư bảo trì', 'Công ty Nhựa Tân Tiến', '2019', '2021', 'Bảo trì phòng ngừa 40 máy ép, giảm 25% thời gian dừng máy.')],
    education: [{ id: 'd1', school: 'Đại học Bách khoa TP.HCM', degree: 'Kỹ thuật cơ khí', from: '2014', to: '2019', desc: '' }],
    skills: sk(['SolidWorks', 5], ['AutoCAD', 5], ['PLC cơ bản', 3], ['Lean / 5S', 4], ['Ansys', 3]), awards: 'Sáng kiến cải tiến cấp công ty 2023', highlights: [{ id: 'h1', value: '+18%', label: 'năng suất' }, { id: 'h2', value: '-12%', label: 'phế phẩm' }, { id: 'h3', value: '5', label: 'năm kinh nghiệm' }], interests: 'Mô hình cơ khí\nBóng đá', }),
  quanly: b('Đỗ Hoàng An', 'Giám đốc Kinh doanh', '10 năm kinh nghiệm quản lý bán hàng và phát triển thị trường, dẫn dắt đội 40 người, đạt và vượt chỉ tiêu doanh số liên tục 5 năm.', {
    address: 'Quận 1, TP. Hồ Chí Minh', website: 'linkedin.com/in/hoangan',
    experience: [e('e1', 'Giám đốc Kinh doanh', 'Công ty CP Phân phối Việt Á', '2019', 'Hiện tại', 'Quản lý đội 40 nhân sự, doanh thu 180 tỷ/năm, tăng trưởng 28%.\nMở rộng mạng lưới sang 12 tỉnh thành, ký hợp đồng với 3 chuỗi bán lẻ lớn.\nXây dựng hệ thống KPI và đào tạo quản lý kế cận.'), e('e2', 'Trưởng phòng Kinh doanh', 'Công ty Hoàng Long', '2014', '2019', 'Phát triển kênh phân phối, tăng gấp đôi doanh số sau 3 năm.')],
    education: [{ id: 'd1', school: 'Đại học Ngoại thương', degree: 'Kinh tế đối ngoại', from: '2008', to: '2012', desc: '' }, { id: 'd2', school: 'CFVG', degree: 'MBA', from: '2016', to: '2018', desc: '' }],
    skills: sk(['Lãnh đạo', 5], ['Chiến lược bán hàng', 5], ['Đàm phán', 5], ['Quản trị KPI', 4]), awards: 'Top 10 Nhà quản lý bán hàng xuất sắc 2022', highlights: [{ id: 'h1', value: '180 tỷ', label: 'doanh thu/năm' }, { id: 'h2', value: '+28%', label: 'tăng trưởng' }, { id: 'h3', value: '40', label: 'nhân sự quản lý' }, { id: 'h4', value: '12', label: 'tỉnh thành' }], interests: 'Golf\nĐọc sách\nMentor khởi nghiệp', }),
  dichvu: b('Mai Thái Hùng', 'Quản lý nhà hàng', '7 năm trong ngành F&B và khách sạn, quản lý vận hành, đào tạo đội ngũ và nâng cao trải nghiệm khách hàng. Năng động, chịu áp lực tốt.', {
    address: 'Quận Hải Châu, Đà Nẵng',
    experience: [e('e1', 'Quản lý nhà hàng', 'Khách sạn Sông Hàn', '2020', 'Hiện tại', 'Vận hành nhà hàng 120 chỗ, đội 25 nhân viên.\nTăng điểm đánh giá khách hàng từ 4.2 lên 4.7 trên các nền tảng.\nKiểm soát chi phí nguyên liệu, giảm 8% hao hụt.'), e('e2', 'Giám sát ca', 'Chuỗi Cafe Nắng', '2017', '2020', 'Điều phối ca, đào tạo nhân viên mới, xử lý phản hồi khách hàng.')],
    education: [{ id: 'd1', school: 'Cao đẳng Du lịch Đà Nẵng', degree: 'Quản trị nhà hàng - khách sạn', from: '2013', to: '2016', desc: '' }],
    skills: sk(['Quản lý ca', 5], ['Chăm sóc khách hàng', 5], ['Đào tạo nhân viên', 4], ['Kiểm soát chi phí', 4]), languages: [{ id: 'l1', name: 'Tiếng Anh', level: 'Giao tiếp' }, { id: 'l2', name: 'Tiếng Hàn', level: 'Cơ bản' }], highlights: [{ id: 'h1', value: '4.7/5', label: 'điểm khách hàng' }, { id: 'h2', value: '25', label: 'nhân viên' }, { id: 'h3', value: '-8%', label: 'hao hụt' }], interests: 'Ẩm thực\nDu lịch\nCà phê rang xay', }),
  sinhvien: b('Ngô Anh Tuấn', 'Sinh viên năm cuối - Thực tập Kinh doanh', 'Sinh viên năm cuối Quản trị kinh doanh, chủ động, học nhanh, có kinh nghiệm hoạt động đoàn thể và bán thời gian. Mong muốn thực tập để áp dụng kiến thức vào thực tế.', {
    address: 'Thủ Đức, TP. Hồ Chí Minh',
    experience: [e('e1', 'Cộng tác viên Marketing', 'Công ty Sao Việt', '06/2024', '09/2024', 'Lên ý tưởng và đăng bài fanpage, tăng 40% tương tác sau 3 tháng.\nHỗ trợ tổ chức 2 sự kiện với hơn 300 người tham dự.'), e('e2', 'Phó ban Truyền thông CLB', 'CLB Kinh doanh trường', '2022', '2024', 'Quản lý đội 8 bạn, thực hiện 10 chương trình trong năm.')],
    education: [{ id: 'd1', school: 'Đại học Kinh tế TP.HCM', degree: 'Quản trị kinh doanh', from: '2021', to: '2025', desc: 'GPA 3.5/4.0' }],
    skills: sk(['Giao tiếp', 4], ['Excel', 4], ['Canva', 4], ['Làm việc nhóm', 5], ['PowerPoint', 4]), languages: [{ id: 'l1', name: 'Tiếng Anh', level: 'IELTS 6.5' }], awards: 'Học bổng khuyến khích học tập 2022-2024', highlights: [{ id: 'h1', value: '3.5', label: 'GPA /4.0' }, { id: 'h2', value: '10', label: 'chương trình tổ chức' }, { id: 'h3', value: '6.5', label: 'IELTS' }], interests: 'Bóng rổ\nTình nguyện\nĐọc sách', }),
};

export const fieldLabel = (id: string) => CV_FIELDS.find((f) => f.id === id)?.label || id;
