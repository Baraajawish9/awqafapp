# نظام إدارة اختبارات الأوقاف

نظام إدارة اختبارات الأوقاف هو تطبيق مبني باستخدام Django لتنظيم لجان اختبار أجزاء القرآن الكريم. يهدف النظام إلى مساعدة الإدارة على إدخال الطلاب وتوزيعهم ومتابعة حالاتهم، ومساعدة لجان الاختبار على تقييم الطلاب، وعرض حالة اللجان على شاشة عامة مناسبة للاستخدام داخل المركز.

تم تصميم الواجهة لتكون عربية واتجاهها من اليمين إلى اليسار، مع دعم الشاشات المكتبية وشاشات العرض العامة وأجهزة الهاتف المستخدمة داخل اللجان.

## فكرة النظام

بدلاً من إدارة الطلاب واللجان يدوياً عبر ملفات منفصلة أو قوائم ورقية، يجمع النظام العمليات الأساسية في مكان واحد:

- إدخال الطلاب أو استيرادهم من ملف Excel.
- توزيع الطلاب على اللجان.
- ترتيب الطلاب داخل كل لجنة.
- متابعة حالة كل طالب أثناء سير الاختبار.
- عرض قوائم الانتظار على شاشة عامة.
- تمكين المقيمين في اللجان من إدخال النتائج.
- تصدير كشوف الطلاب والنتائج عند الحاجة.

## المستخدمون المستهدفون

### الإدارة

تستخدم الإدارة لوحة التحكم لإضافة الطلاب، استيراد ملفات Excel، ضبط عدد اللجان وإعدادات الشاشة، متابعة قوائم اللجان، تعديل حالة الطالب، نقل الطالب بين اللجان، وتصدير الكشوف.

### المقيمون داخل اللجان

يدخل المقيم إلى صفحة اللجنة الخاصة به، يرى الطلاب المرتبطين بلجنته، يفتح نموذج تقييم الطالب الجاري اختباره أو الطالب المتأخر، ثم يرسل النتيجة.

### شاشة العرض العامة

تعرض الشاشة العامة حالة اللجان والطلاب بشكل واضح للحضور أو المشرفين، مع تنظيم تلقائي يناسب عدد اللجان وحجم الشاشة.

## الميزات الرئيسية

- واجهة عربية RTL مناسبة لطبيعة الاستخدام داخل المركز.
- لوحة إدارة للطلاب واللجان.
- إضافة طالب يدوياً مع بيانات الاسم، الأب، سنة الميلاد، المعهد، نوع الاختبار، الأجزاء، واللجنة.
- استيراد الطلاب من ملف Excel.
- ربط الأجزاء المحفوظة بلجان محددة أثناء الاستيراد.
- توزيع تلقائي للطلاب على اللجان الأقل ازدحاماً.
- إدارة الطلاب غير الموزعين بعد الاستيراد.
- نقل الطالب بين اللجان أو تغيير ترتيبه داخل اللجنة.
- تحديث حالة الطالب بين: في الاختبار، انتظار، قائمة الانتظار، متأخر، منتهي.
- تطبيق تحديث تلقائي لحالات الطلاب داخل كل لجنة حسب ترتيب الانتظار.
- فلترة وبحث في الطلاب حسب الاسم أو الرقم أو اللجنة أو الحالة.
- ملخص سريع لكل لجنة يتضمن العدد، المنتظرين، المتأخرين، والطالب الجاري اختباره.
- شاشة عامة لعرض حالة اللجان.
- أنماط عرض مختلفة للشاشة العامة حسب عدد اللجان.
- وضع نافذة زمنية يعرض طلاب الفترة الحالية.
- عرض النتائج الحديثة لفترة محددة بعد انتهاء التقييم.
- صفحات مخصصة للمقيمين داخل اللجان.
- نموذج تقييم منفصل حسب نوع الاختبار.
- منع تعديل نتيجة الطالب بعد إنهاء اختباره.
- تصدير كشوف Excel للطلاب.
- تصدير كشوف Excel مع الدرجات والنتائج.
- حساب الوقت المتوقع للطلاب داخل الكشوف.
- دعم الوضع الفاتح والداكن حسب نطاق كل شاشة.

## صفحات النظام

- `/`: صفحة تسجيل الدخول.
- `/dashboard/`: لوحة إدارة الطلاب واللجان.
- `/display/`: الشاشة العامة.
- `/settings/`: إعدادات النظام والشاشة.
- `/contact/`: صفحة تواصل منفصلة للدعم أو الملاحظات.
- `/rooms/<room_name>/<subroom>/`: صفحة لجنة فرعية للمقيم.
- `/rooms/<room_name>/<subroom>/students/<student_number>/grade/`: صفحة تقييم طالب.

## حالات الطلاب

يعتمد النظام على حالات واضحة لمتابعة سير الاختبار:

- `in_exam`: الطالب داخل الاختبار حالياً.
- `waiting`: الطالب ضمن قائمة الانتظار القريبة.
- `on_waiting_list`: الطالب موجود في قائمة الانتظار العامة.
- `late`: الطالب متأخر.
- `finished`: الطالب أنهى الاختبار.

هذه الحالات تظهر في لوحة الإدارة، شاشة العرض العامة، وصفحات اللجان، وتستخدم أيضاً في ترتيب الطلاب تلقائياً.

## الاستيراد والتصدير

يدعم النظام استيراد الطلاب من ملفات Excel، مع إمكانية تحديد لجان مفضلة لأجزاء معينة. بعد الاستيراد يمكن للإدارة توزيع الطلاب دفعة واحدة أو توزيع كل طالب على حدة.

يدعم النظام أيضاً تصدير كشوف Excel. يمكن تصدير كشف الطلاب فقط، أو كشف يتضمن الدرجات والنتائج النهائية. كما يضيف النظام الوقت المتوقع للطلاب بناءً على إعدادات بداية الاختبار والمدة المتوقعة لكل طالب.

## شاشة العرض العامة

صممت الشاشة العامة للاستخدام على شاشة كبيرة داخل المركز. تعرض اللجان والطلاب بحجم مناسب، وتغير كثافة العرض تلقائياً حسب عدد اللجان. كما تدعم وضعاً يعرض طلاب الفترة الحالية فقط، وهو مفيد عند الحاجة إلى شاشة أكثر تركيزاً على الوقت الحالي.

## التقييم والنتائج

يدعم النظام نوعين من نماذج التقييم بحسب نوع الاختبار. عند إدخال نتائج الفروع المطلوبة، يحسب النظام النتيجة النهائية، يحفظها، ثم يغير حالة الطالب إلى منتهي. كما تظهر النتيجة الحديثة مؤقتاً على الشاشة العامة حسب مدة العرض المحددة في الإعدادات.

## بنية المشروع

- `awqaf/`: إعدادات مشروع Django والروابط العامة.
- `login/`: تسجيل الدخول، مستخدمو اللجان، وعمليات الدخول والخروج.
- `screen/`: لوحة الإدارة، الشاشة العامة، الإعدادات، الاستيراد، التصدير، الحالات، وصفحة التواصل.
- `mobileapp/`: صفحات اللجان ونماذج تقييم الطلاب.
- `screen/templates/`: قوالب واجهات الإدارة والشاشة العامة وصفحة التواصل.
- `mobileapp/templates/`: قوالب صفحات اللجان والتقييم.
- `screen/static/screen/ui.css`: ملف التصميم المشترك.
- `screen/static/screen/theme.js`: منطق تبديل الوضع الفاتح والداكن.
- `db.sqlite3`: قاعدة بيانات SQLite المحلية.
- `grades_log.csv`: سجل محلي للدرجات النهائية عند حفظها.

## التشغيل محلياً

من مجلد المشروع:

```powershell
python manage.py runserver 127.0.0.1:8000
```

ثم افتح:

```text
http://127.0.0.1:8000/
```

## التحقق

تم التحقق من حالة المشروع باستخدام:

```powershell
python manage.py check
```

يعني ذلك أن Django يستطيع تحميل الإعدادات والروابط والتطبيقات بدون أخطاء في فحص النظام.

## معلومات التواصل

- تيليغرام: [@Bjawish](https://t.me/Bjawish)
- البريد الإلكتروني: [baraaj2009@gmail.com](mailto:baraaj2009@gmail.com)

---

# Awqaf Exam Management System

Awqaf Exam Management System is a Django application for organizing Quran-part exam committees. It helps administrators manage students, room queues, statuses, public display screens, evaluator workflows, grading, exports, and system settings from one Arabic right-to-left interface.

The app is built for practical use inside an exam center: administrators work from the dashboard, evaluators use room-specific mobile pages, and the public screen shows queue and status information clearly.

## System Purpose

The application replaces scattered manual tracking with a single workflow:

- Add or import students.
- Assign students to exam rooms.
- Manage room order and waiting lists.
- Track each student's status during the exam.
- Display live room queues on a public screen.
- Let evaluators submit grades from room pages.
- Export student lists and final results to Excel.

## Target Users

### Administrators

Administrators use the dashboard to add students, import Excel sheets, configure room counts and display settings, monitor all rooms, change student statuses, move students, and export reports.

### Room Evaluators

Evaluators log in to their assigned room view, see their room queue, open the active or late student, fill the grading form, and submit the result.

### Public Display

The public display shows room queues and student statuses in a format suitable for large screens in the exam center.

## Main Features

- Arabic RTL interface for operational use.
- Student and room administration dashboard.
- Manual student creation with name, father name, birth year, institute, exam type, memorized parts, and room.
- Excel student import.
- Import mapping between memorized parts and preferred rooms.
- Automatic assignment to the least-loaded room.
- Management of imported students waiting for assignment.
- Student movement between rooms and within room order.
- Student status updates: in exam, waiting, waiting list, late, and finished.
- Automatic status application based on room queue order.
- Search and filtering by name, number, room, and status.
- Room summary cards with totals, waiting count, late count, and current student.
- Public display screen for room status.
- Multiple public screen density layouts based on room count.
- Time-window display mode for the current exam period.
- Recent result display after final grading.
- Room-specific evaluator pages.
- Separate grading forms based on exam type.
- Protection against editing a student after the exam is finished.
- Excel export for student lists.
- Excel export with grades and final results.
- Expected time calculation in exported sheets.
- Light and dark theme support per screen scope.

## Application Pages

- `/`: Login page.
- `/dashboard/`: Student and room administration dashboard.
- `/display/`: Public display screen.
- `/settings/`: System and display settings.
- `/contact/`: Separate support/contact page.
- `/rooms/<room_name>/<subroom>/`: Evaluator sub-room page.
- `/rooms/<room_name>/<subroom>/students/<student_number>/grade/`: Student grading page.

## Student Statuses

The system uses clear statuses to track the exam flow:

- `in_exam`: The student is currently inside the exam.
- `waiting`: The student is in the near waiting group.
- `on_waiting_list`: The student is in the general waiting list.
- `late`: The student is late.
- `finished`: The student has completed the exam.

These statuses are used across the admin dashboard, public display, evaluator pages, and automatic ordering logic.

## Import And Export

The app supports Excel imports with optional assignment rules. Administrators can map memorized parts to preferred room groups during import. Imported students can then be assigned individually or in bulk.

The app also supports Excel exports. Administrators can export student lists only, or include grades and final results. Exported sheets include expected timing based on configured exam start time and estimated minutes per student.

## Public Display

The public screen is designed for large displays. It adapts its density based on the number of rooms and can show either room-based queues or a focused current-time-window view. Recent final results can appear temporarily after grading.

## Grading And Results

The system supports grading workflows for different exam types. Once the required branch results are submitted, the app calculates the final result, saves it, marks the student as finished, and can show the recent result on the public display for a configured duration.

## Project Structure

- `awqaf/`: Django project settings and root URLs.
- `login/`: Login flow, room users, and authentication helpers.
- `screen/`: Dashboard, public display, settings, import/export, statuses, and contact page.
- `mobileapp/`: Evaluator room views and grading workflows.
- `screen/templates/`: Dashboard, public display, settings, and contact templates.
- `mobileapp/templates/`: Room and grading templates.
- `screen/static/screen/ui.css`: Shared styling.
- `screen/static/screen/theme.js`: Light/dark theme switching.
- `db.sqlite3`: Local SQLite database.
- `grades_log.csv`: Local final-grade log.

## Running Locally

From the project directory:

```powershell
python manage.py runserver 127.0.0.1:8000
```

Then open:

```text
http://127.0.0.1:8000/
```

## Validation

The project was checked with:

```powershell
python manage.py check
```

This confirms Django can load the settings, routes, apps, and templates without system-check errors.

## Contact

- Telegram: [@Bjawish](https://t.me/Bjawish)
- Email: [baraaj2009@gmail.com](mailto:baraaj2009@gmail.com)
