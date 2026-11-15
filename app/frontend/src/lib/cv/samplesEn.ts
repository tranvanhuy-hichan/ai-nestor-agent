import { SAMPLE_PHOTO, type CvData } from './types';
import { FIELD_SAMPLES, b, e, sk, type CvFieldId } from './fields';
import type { CvLang } from './i18n';

/** English counterparts of the sample CVs (same people, same layout of facts), used when the CV language is English. */
const base = (name: string, title: string, summary: string, rest: Partial<CvData>): CvData => ({
  ...b(name, title, summary, { languages: [{ id: 'l1', name: 'English', level: 'Fluent' }], address: 'Ho Chi Minh City, Vietnam', ...rest }),
  email: 'contact@email.com', phone: '+84 912 345 678', photo: SAMPLE_PHOTO,
});
const edu = (school: string, degree: string, from: string, to: string, desc = '') => [{ id: 'd1', school, degree, from, to, desc }];

export const SAMPLE_CV_EN: CvData = base('Minh Anh Nguyen', 'Frontend Developer', 'Over 4 years building web applications for e-commerce and fintech. Comfortable in Agile teams, focused on user experience, performance and maintainable code. Looking for a Senior Frontend role leading a small team.', {
  email: 'minhanh@email.com', phone: '+84 901 234 567', website: 'linkedin.com/in/minhanh',
  experience: [
    e('e1', 'Frontend Developer', 'Sanviet Joint Stock Company', '03/2022', 'Present', 'Rebuilt the checkout flow with React and Next.js, cutting page load time by 35%.\nLed a team of 3: code reviews and onboarding of new members.\nIntegrated payment gateways, raising order completion by 12%.'),
    e('e2', 'Web Developer', 'Ha Long Studio', '07/2020', '02/2022', 'Delivered 20+ corporate websites with JavaScript and WordPress.\nStandardised a shared UI library used across 5 projects.'),
  ],
  education: edu('Ho Chi Minh City University of Technology', 'B.Eng. in Information Technology', '2016', '2020', 'GPA 3.4/4.0, academic scholarship for 3 semesters.'),
  skills: sk(['React / Next.js', 5], ['TypeScript', 5], ['HTML / CSS', 5], ['Node.js', 4], ['Figma', 3], ['Git / CI-CD', 4]),
  languages: [{ id: 'l1', name: 'English', level: 'IELTS 7.0' }, { id: 'l2', name: 'Japanese', level: 'N4' }],
  projects: [{ id: 'p1', name: 'Retail management system', desc: 'Web app for 40 stores, 10,000+ orders per month.' }],
  awards: 'Outstanding Employee 2023\nAWS Cloud Practitioner certificate',
  highlights: [{ id: 'h1', value: '4+', label: 'years of experience' }, { id: 'h2', value: '20+', label: 'projects delivered' }, { id: 'h3', value: '-35%', label: 'page load time' }],
  interests: 'Open source\nChess\nRunning',
});

export const FIELD_SAMPLES_EN: Record<CvFieldId, CvData> = {
  cntt: SAMPLE_CV_EN,
  thietke: base('Tu Quynh Hoang', 'Graphic Designer', '5+ years designing brand identities, print and digital interfaces. Loves visual storytelling, works well in teams and always meets deadlines.', {
    website: 'behance.net/tuquynh',
    experience: [e('e1', 'Senior Graphic Designer', 'Hoa Sen Agency', '2021', 'Present', 'Led identity design for 30+ F&B and fashion brands.\nBuilt a design system that cut handover time by 40%.'), e('e2', 'Graphic Designer', 'May Studio', '2018', '2021', 'Designed posters, banners, packaging and product photo sets for local clients.')],
    education: edu('University of Industrial Fine Arts', 'Graphic Design', '2014', '2018'),
    skills: sk(['Photoshop', 5], ['Illustrator', 5], ['Figma', 4], ['After Effects', 3], ['Typography', 5]),
    projects: [{ id: 'p1', name: 'Nang coffee chain rebrand', desc: '25% more returning customers within 6 months of launch.' }], awards: 'Silver Award, Vietnam Design Awards 2023',
    highlights: [{ id: 'h1', value: '5+', label: 'years designing' }, { id: 'h2', value: '30+', label: 'brands' }, { id: 'h3', value: '-40%', label: 'handover time' }], interests: 'Illustration\nStreet photography\nHandmade ceramics',
  }),
  marketing: base('My Linh Pham', 'Marketing Specialist', '4 years of digital marketing for retail and e-commerce. Strong at data analysis, ad cost optimisation and conversion-focused content.', {
    website: 'linkedin.com/in/mylinh',
    experience: [e('e1', 'Digital Marketing Executive', 'An Phat Joint Stock Company', '2022', 'Present', 'Managed a 300M VND/month ad budget on Meta and Google.\nGrew online revenue 62% in 12 months and cut cost per order by 20%.\nRan 15 campaigns with the content and design teams.'), e('e2', 'Content Marketer', 'Moc Lan Co., Ltd', '2020', '2022', 'Wrote SEO articles and short-video scripts, tripling organic traffic.')],
    education: edu('National Economics University', 'Marketing', '2016', '2020'),
    skills: sk(['Facebook Ads', 5], ['Google Analytics', 4], ['SEO', 4], ['Content', 5], ['Canva', 4]), awards: 'Employee of the Quarter, Q3 2023',
    highlights: [{ id: 'h1', value: '+62%', label: 'online revenue' }, { id: 'h2', value: '-20%', label: 'cost per order' }, { id: 'h3', value: '15', label: 'campaigns' }, { id: 'h4', value: '300M', label: 'monthly budget' }], interests: 'Business books\nTravel\nYoga',
  }),
  taichinh: base('Ngoc Bich Le', 'General Accountant', '6 years in general accounting, financial reporting and tax filing for manufacturers. Careful, honest and fluent in accounting software.', {
    address: 'Da Nang, Vietnam',
    experience: [e('e1', 'General Accountant', 'Nam Viet Equipment JSC', '2019', 'Present', 'Prepared monthly, quarterly and annual financial and tax reports.\nReconciled payables and receivables, keeping ledger discrepancies under 1%.\nWorked with external auditors and tax authorities.'), e('e2', 'Accountant', 'Hai Dang Co., Ltd', '2017', '2019', 'Recorded receipts and payments, tracked fixed assets and payroll.')],
    education: edu('Danang University of Economics', 'Corporate Accounting', '2013', '2017', 'Graduated with Distinction'),
    skills: sk(['MISA', 5], ['Advanced Excel', 5], ['Tax reporting', 5], ['Management accounting', 4]), awards: 'Chief Accountant certificate\nACCA F1-F3',
    highlights: [{ id: 'h1', value: '6', label: 'years of experience' }, { id: 'h2', value: '<1%', label: 'ledger discrepancies' }, { id: 'h3', value: '2', label: 'international certificates' }], interests: 'Finance books\nBadminton',
  }),
  nhansu: base('Thu Lan Nguyen', 'HR Specialist', '5 years in recruitment and HR administration. Strong communicator who builds onboarding processes and company culture, knowledgeable in labour law.', {
    experience: [e('e1', 'HR Executive', 'Sao Mai Group', '2021', 'Present', 'Hired 120+ office and sales staff per year.\nBuilt an onboarding process that cut first-3-month attrition by 30%.\nManaged employee records, insurance and labour contracts.'), e('e2', 'Recruiter', 'Thanh Cong Company', '2019', '2021', 'Posted jobs, screened CVs, interviewed and negotiated offers.')],
    education: edu('University of Labour and Social Affairs', 'Human Resource Management', '2015', '2019'),
    skills: sk(['Recruitment', 5], ['Labour law', 4], ['C&B', 4], ['Training', 4], ['Excel', 4]),
    highlights: [{ id: 'h1', value: '120+', label: 'hires per year' }, { id: 'h2', value: '-30%', label: 'early attrition' }, { id: 'h3', value: '5', label: 'years of experience' }], interests: 'Event planning\nVolunteering\nCooking',
  }),
  yte: base('Hanh Tran', 'Registered Nurse', '5 years as a nurse in a general internal medicine ward: dedicated, resilient under pressure and skilled in comprehensive patient care. Seeking a high-quality healthcare facility.', {
    address: 'Can Tho, Vietnam',
    experience: [e('e1', 'Internal Medicine Nurse', 'Can Tho General Hospital', '2020', 'Present', 'Cared for and monitored 15-20 patients per shift, carrying out orders accurately.\nTrained new nurses and student interns.\nTook part in emergency and resuscitation procedures.'), e('e2', 'Staff Nurse', 'Tam An Clinic', '2018', '2020', 'Reception, injections and lab sample collection.')],
    education: edu('Can Tho University of Medicine and Pharmacy', 'B.Sc. in Nursing', '2014', '2018'),
    skills: sk(['Patient care', 5], ['First aid', 5], ['Medical records', 4], ['Communication', 5]), awards: 'Nursing practice licence\nBLS certificate',
    highlights: [{ id: 'h1', value: '5', label: 'years clinical' }, { id: 'h2', value: '15-20', label: 'patients per shift' }, { id: 'h3', value: '2', label: 'licences' }], interests: 'Medical volunteering\nReading\nWalking',
  }),
  kythuat: base('Duc Minh Vu', 'Mechanical Engineer', 'Mechanical engineer with 5 years designing and improving production lines. Skilled in CAD/CAM, focused on cost optimisation and workplace safety.', {
    address: 'Bien Hoa, Dong Nai',
    experience: [e('e1', 'Design Engineer', 'Dai Phat Mechanical Co.', '2021', 'Present', 'Designed machine parts and fixtures in SolidWorks and AutoCAD.\nImproved machining, raising productivity 18% and cutting scrap 12%.\nSupervised installation and acceptance at client plants.'), e('e2', 'Maintenance Engineer', 'Tan Tien Plastics', '2019', '2021', 'Preventive maintenance of 40 injection machines, cutting downtime 25%.')],
    education: edu('Ho Chi Minh City University of Technology', 'Mechanical Engineering', '2014', '2019'),
    skills: sk(['SolidWorks', 5], ['AutoCAD', 5], ['Basic PLC', 3], ['Lean / 5S', 4], ['Ansys', 3]), awards: 'Company improvement initiative award 2023',
    highlights: [{ id: 'h1', value: '+18%', label: 'productivity' }, { id: 'h2', value: '-12%', label: 'scrap' }, { id: 'h3', value: '5', label: 'years of experience' }], interests: 'Mechanical models\nFootball',
  }),
  quanly: base('Hoang An Do', 'Sales Director', '10 years managing sales and developing markets, leading a team of 40 and beating sales targets for 5 consecutive years.', {
    website: 'linkedin.com/in/hoangan',
    experience: [e('e1', 'Sales Director', 'Viet A Distribution JSC', '2019', 'Present', 'Lead 40 staff, 180B VND annual revenue, 28% growth.\nExpanded the network to 12 provinces and signed 3 major retail chains.\nBuilt the KPI system and trained successor managers.'), e('e2', 'Head of Sales', 'Hoang Long Company', '2014', '2019', 'Developed distribution channels, doubling sales in 3 years.')],
    education: [{ id: 'd1', school: 'Foreign Trade University', degree: 'International Economics', from: '2008', to: '2012', desc: '' }, { id: 'd2', school: 'CFVG', degree: 'MBA', from: '2016', to: '2018', desc: '' }],
    skills: sk(['Leadership', 5], ['Sales strategy', 5], ['Negotiation', 5], ['KPI management', 4]), awards: 'Top 10 Sales Managers 2022',
    highlights: [{ id: 'h1', value: '180B', label: 'annual revenue' }, { id: 'h2', value: '+28%', label: 'growth' }, { id: 'h3', value: '40', label: 'people managed' }, { id: 'h4', value: '12', label: 'provinces' }], interests: 'Golf\nReading\nMentoring startups',
  }),
  dichvu: base('Thai Hung Mai', 'Restaurant Manager', '7 years in F&B and hospitality: operations, team training and customer experience. Energetic and calm under pressure.', {
    address: 'Da Nang, Vietnam',
    experience: [e('e1', 'Restaurant Manager', 'Song Han Hotel', '2020', 'Present', 'Run a 120-seat restaurant with a team of 25.\nRaised customer ratings from 4.2 to 4.7 across platforms.\nControlled ingredient costs, reducing waste by 8%.'), e('e2', 'Shift Supervisor', 'Nang Cafe Chain', '2017', '2020', 'Scheduled shifts, trained new staff and handled customer feedback.')],
    education: edu('Da Nang Tourism College', 'Restaurant & Hotel Management', '2013', '2016'),
    skills: sk(['Shift management', 5], ['Customer care', 5], ['Staff training', 4], ['Cost control', 4]), languages: [{ id: 'l1', name: 'English', level: 'Conversational' }, { id: 'l2', name: 'Korean', level: 'Basic' }],
    highlights: [{ id: 'h1', value: '4.7/5', label: 'customer rating' }, { id: 'h2', value: '25', label: 'staff' }, { id: 'h3', value: '-8%', label: 'waste' }], interests: 'Food\nTravel\nHome-roasted coffee',
  }),
  sinhvien: base('Anh Tuan Ngo', 'Final-year student, Business Intern', 'Final-year Business Administration student: proactive, quick learner, with experience in student organisations and part-time work. Seeking an internship to apply what I have learned.', {
    address: 'Thu Duc, Ho Chi Minh City',
    experience: [e('e1', 'Marketing Collaborator', 'Sao Viet Company', '06/2024', '09/2024', 'Planned and posted fanpage content, lifting engagement 40% in 3 months.\nHelped run 2 events with 300+ attendees.'), e('e2', 'Vice Head of Media, Business Club', 'University Business Club', '2022', '2024', 'Managed a team of 8 and delivered 10 programmes a year.')],
    education: edu('University of Economics Ho Chi Minh City', 'Business Administration', '2021', '2025', 'GPA 3.5/4.0'),
    skills: sk(['Communication', 4], ['Excel', 4], ['Canva', 4], ['Teamwork', 5], ['PowerPoint', 4]), languages: [{ id: 'l1', name: 'English', level: 'IELTS 6.5' }], awards: 'Academic scholarship 2022-2024',
    highlights: [{ id: 'h1', value: '3.5', label: 'GPA /4.0' }, { id: 'h2', value: '10', label: 'programmes organised' }, { id: 'h3', value: '6.5', label: 'IELTS' }], interests: 'Basketball\nVolunteering\nReading',
  }),
};

/** The sample CVs in the chosen CV language. */
export const fieldSamples = (lang?: CvLang) => (lang === 'en' ? FIELD_SAMPLES_EN : FIELD_SAMPLES);
/** Which industry a CV's text still matches as an untouched sample (either language), if any. */
export const sampleField = (d: CvData): CvFieldId | null =>
  ((Object.keys(FIELD_SAMPLES) as CvFieldId[]).find((k) => [FIELD_SAMPLES[k], FIELD_SAMPLES_EN[k]].some((s) => s.summary === d.summary && s.name === d.name)) ?? null);
