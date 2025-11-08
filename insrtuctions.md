# CLAUDE CODE CONTEXT PROMPT - GREENTRACK PROJECT

## ROLE & MISSION

You are an elite Odoo 19 developer helping build **GreenTrack - AI-Powered Carbon Intelligence Platform** for a 2-day hackathon. Your goal is to provide expert guidance, complete code implementations, and help execute a stage-by-stage build plan to create a winning CSR & Sustainability tracking application.

---

## HACKATHON CONTEXT

### The Challenge
Companies in the UAE are expected to actively contribute to building a better and more sustainable future by reducing emissions, supporting communities, and aligning with **Net Zero 2050** and the **UN Sustainable Development Goals (SDGs)**. 

**Task:** Design and develop an Odoo app that empowers organizations to plan, manage, and measure the impact of their CSR and sustainability initiatives.

### Hackathon Requirements (MUST MEET)

**Minimum Technical Requirements:**
- ✅ At least **3 models** (e.g., CSR Program, Project, Activity)
- ✅ Minimum **3 view types**: List, Form, and Kanban
- ✅ Standard Odoo components (no base color/font modifications)
- ✅ Working module with demo data
- ✅ 3-5 minute live demo

**Judging Criteria (Weighted):**
- Core Functionality (30%) - Quality and reliability
- Innovation and Creativity (25%) - Originality and smart features
- User Experience (20%) - Ease of use, clarity, design
- Data and Impact Metrics (15%) - Accuracy and insightful KPIs
- Presentation and Storytelling (10%) - Demo clarity

### Areas for Innovation (MUST INCLUDE)
- ✅ Integrate APIs for real-world data
- ✅ Build upon existing Odoo modules (HR, Accounting, Projects, CRM)
- ✅ Add intelligent features (dashboards, analytics, gamification)
- ✅ Implement AI/ML functionality (predictive analytics)
- ✅ Use Python creatively for KPI computation

---

## PROJECT OVERVIEW

### Project Name
**GreenTrack - AI-Powered Carbon Intelligence Platform**

### Tagline
"From Measurement to Net Zero - Smart Carbon Management for UAE Enterprises"

### Core Value Proposition
- **Track Everything:** Log all carbon-generating activities (electricity, travel, paper, waste, etc.)
- **See Impact:** Dashboard shows "You saved 500 kg CO2 = 24 trees planted"
- **Motivate Staff:** Leaderboard makes sustainability fun (gamification)
- **Generate Reports:** Automatic CSR compliance reports and SDG alignment

### Why This Wins
1. **Most Ambitious Scope** - API + AI + Gamification + Dashboard
2. **Real-World Value** - Helps UAE companies reach Net Zero 2050
3. **Technical Depth** - Showcases advanced Odoo skills
4. **Beautiful UX** - Dashboard-first design with professional analytics
5. **Complete Solution** - Not just tracking, but insights and predictions

---

## DATABASE ARCHITECTURE

### Model Relationships
```
carbon.initiative (The Green Programs)
    ↓ One2many: activity_ids
carbon.activity (The Emission Events)
    ↑ Many2one: initiative_id
    ↓ Many2one: employee_id (res.users)

carbon.initiative
    ↓ One2many: goal_ids
carbon.goal (The Milestones)
    ↑ Many2one: initiative_id
```

### Model 1: carbon.initiative

**Purpose:** Represents CSR environmental programs/projects

**Python Model Definition:**
```python
class CarbonInitiative(models.Model):
    _name = "carbon.initiative"
    _description = "Carbon Reduction Initiative"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "start_date desc"
```

**Fields:**

| Field Name | Type | Required | Attributes | Description |
|------------|------|----------|------------|-------------|
| name | Char | Yes | tracking=True | Initiative name |
| description | Text | No | | What is this initiative about? |
| category | Selection | Yes | tracking=True | energy, waste, transport, office, water |
| start_date | Date | Yes | | Program start date |
| end_date | Date | No | | Program end date |
| state | Selection | Yes | default='draft', tracking=True | draft, active, completed, cancelled |
| target_co2_reduction | Float | Yes | | Goal: Reduce X kg CO2 |
| actual_co2_reduction | Float | No | compute='_compute_actual_reduction', store=True | Actually reduced (from activities) |
| progress_percentage | Float | No | compute='_compute_progress', store=True | (actual/target) * 100 |
| activity_ids | One2many | No | 'carbon.activity', 'initiative_id' | Related activities |
| goal_ids | One2many | No | 'carbon.goal', 'initiative_id' | Related goals |
| color | Integer | No | | For Kanban color coding |
| activity_count | Integer | No | compute='_compute_activity_count' | Number of activities |

**Computed Methods Required:**
- `_compute_actual_reduction()` - Sum of all activity.co2_saved
- `_compute_progress()` - (actual/target) * 100
- `_compute_activity_count()` - Count of activities

---

### Model 2: carbon.activity

**Purpose:** Individual carbon-generating or carbon-saving events

**Python Model Definition:**
```python
class CarbonActivity(models.Model):
    _name = "carbon.activity"
    _description = "Carbon Activity"
    _order = "activity_date desc"
```

**Fields:**

| Field Name | Type | Required | Attributes | Description |
|------------|------|----------|------------|-------------|
| name | Char | No | compute='_compute_name', store=True | Auto-generated description |
| activity_type | Selection | Yes | | electricity, fuel, paper, travel, waste, water |
| activity_date | Date | Yes | default=fields.Date.context_today | When did this happen? |
| quantity | Float | Yes | | How much? (100 kWh, 50 liters, etc.) |
| unit | Selection | Yes | | kwh, liters, kg, km, sheets |
| emission_factor | Float | No | | kg CO2 per unit (from API or preset) |
| co2_generated | Float | No | compute='_compute_co2', store=True | quantity * emission_factor |
| co2_saved | Float | No | | For reduction activities (positive value) |
| initiative_id | Many2one | No | 'carbon.initiative', ondelete='cascade' | Link to initiative |
| employee_id | Many2one | No | 'res.users' | Link to user/employee |
| source | Selection | No | default='manual' | manual, api, system |

**Computed Methods Required:**
- `_compute_name()` - Auto-generate name from type, quantity, date
- `_compute_co2()` - quantity * emission_factor

**Onchange Methods Required:**
- `_onchange_activity_type()` - Auto-fill emission_factor from API or defaults

**Default Emission Factors (UAE Standards):**
```python
EMISSION_FACTORS = {
    'electricity': 0.45,  # kg CO2/kWh
    'fuel': 2.31,         # kg CO2/liter gasoline
    'paper': 0.01,        # kg CO2/sheet
    'travel': 0.12,       # kg CO2/km (car)
    'waste': 0.5,         # kg CO2/kg
    'water': 0.0003,      # kg CO2/liter
}
```

---

### Model 3: carbon.goal

**Purpose:** Reduction targets and milestones

**Python Model Definition:**
```python
class CarbonGoal(models.Model):
    _name = "carbon.goal"
    _description = "Carbon Reduction Goal"
    _order = "target_date desc"
```

**Fields:**

| Field Name | Type | Required | Attributes | Description |
|------------|------|----------|------------|-------------|
| name | Char | Yes | | Goal name |
| description | Text | No | | Goal description |
| target_date | Date | Yes | | Deadline |
| target_co2_reduction | Float | Yes | | Goal: X kg CO2 |
| actual_co2_reduction | Float | No | compute='_compute_actual', store=True | Progress (from initiative activities) |
| achievement_percentage | Float | No | compute='_compute_achievement', store=True | (actual/target) * 100 |
| state | Selection | No | compute='_compute_state', store=True | pending, in_progress, achieved, missed |
| initiative_id | Many2one | Yes | 'carbon.initiative', required=True, ondelete='cascade' | Link to initiative |
| reward_points | Integer | No | default=100 | Gamification points |

**Computed Methods Required:**
- `_compute_actual()` - Sum initiative activities up to target_date
- `_compute_achievement()` - (actual/target) * 100
- `_compute_state()` - Determine based on achievement and date

---

## PROJECT STRUCTURE

```
greentrack_carbon/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── carbon_initiative.py
│   ├── carbon_activity.py
│   └── carbon_goal.py
├── views/
│   ├── carbon_initiative_views.xml
│   ├── carbon_activity_views.xml
│   ├── carbon_goal_views.xml
│   ├── dashboard_views.xml
│   └── menu.xml
├── data/
│   ├── emission_factors_data.xml
│   ├── demo_data.xml
│   └── cron_jobs.xml
├── security/
│   └── ir.model.access.csv
├── wizards/
│   ├── __init__.py
│   └── carbon_prediction_wizard.py
└── static/
    └── description/
        ├── icon.png
        └── index.html
```

---

## STAGE-BY-STAGE BUILD PLAN

### STAGE 1: Project Setup & Core Models
**Duration:** 2 hours  
**Priority:** CRITICAL - Foundation for everything

**Files to Create:**
1. `__manifest__.py` - Module metadata
2. `models/__init__.py` - Model imports
3. `models/carbon_initiative.py` - Initiative model
4. `models/carbon_activity.py` - Activity model
5. `models/carbon_goal.py` - Goal model
6. `security/ir.model.access.csv` - Access rights

**Key Requirements:**
- All models must have proper `_name`, `_description`, `_order`
- Initiative inherits `mail.thread` and `mail.activity.mixin` for chatter
- All computed fields must have `@api.depends` decorators
- All Many2one fields should have `ondelete='cascade'` where appropriate

**Testing Criteria:**
- Module installs without errors
- All 3 models appear in Settings > Technical > Database Structure > Models
- Can create records via Odoo shell

---

### STAGE 2: Basic Views (List, Form, Kanban)
**Duration:** 2-3 hours  
**Priority:** CRITICAL - Required for demo

**Files to Create:**
1. `views/carbon_initiative_views.xml` - List, Form, Kanban, Action
2. `views/carbon_activity_views.xml` - List, Form, Action
3. `views/carbon_goal_views.xml` - List, Form, Action
4. `views/menu.xml` - Navigation structure

**Key View Features:**

**Initiative Kanban:**
- Group by `state`
- Show progress bar using `progress_percentage`
- Color-coded cards using `color` field
- Display CO2 metrics

**Initiative Form:**
- Header with statusbar widget for `state`
- Smart button for activities (shows `activity_count`)
- Two-column group layout
- Notebook with tabs: Description, Activities, Goals, Chatter
- Activities embedded as editable list
- Goals embedded as editable list

**Activity List:**
- Filterable by `activity_type`
- Sum totals for `co2_saved`
- Date range filters

**Menu Structure:**
```
GreenTrack (Root)
├── Dashboard
├── Initiatives
├── Activities
└── Goals
```

**Testing Criteria:**
- All views render correctly
- Kanban drag-and-drop works
- Smart buttons navigate correctly
- Embedded lists are editable
- Chatter appears and works

---

### STAGE 3: Dashboard & Analytics
**Duration:** 2-3 hours  
**Priority:** HIGH - Major demo impact

**Files to Create:**
1. `views/dashboard_views.xml` - Graph, Pivot, Dashboard views

**Required Chart Types:**

**1. Line Chart - CO2 Trend Over Time**
```xml
<graph type="line">
    <field name="activity_date" interval="month"/>
    <field name="co2_saved" type="measure"/>
</graph>
```

**2. Pie Chart - Emissions by Category**
```xml
<graph type="pie">
    <field name="activity_type"/>
    <field name="co2_saved" type="measure"/>
</graph>
```

**3. Bar Chart - Initiative Comparison**
```xml
<graph type="bar">
    <field name="initiative_id"/>
    <field name="co2_saved" type="measure"/>
</graph>
```

**4. Pivot Table - Multi-dimensional Analysis**
```xml
<pivot>
    <field name="activity_date" interval="month" type="row"/>
    <field name="activity_type" type="col"/>
    <field name="co2_saved" type="measure"/>
</pivot>
```

**Dashboard Action:**
- Opens with graph view by default
- Allows switching between graph types
- Includes pivot table
- Has intelligent search panel

**Testing Criteria:**
- Charts display with demo data
- Can switch between view modes
- Filters work correctly
- Totals calculate accurately

---

### STAGE 4: API Integration
**Duration:** 2 hours  
**Priority:** MEDIUM - Innovation differentiator

**Files to Modify:**
1. `models/carbon_activity.py` - Add API methods
2. `data/cron_jobs.xml` - Scheduled action

**Implementation Requirements:**

**API Integration Method:**
```python
def fetch_emission_factor_from_api(self, activity_type, country='UAE'):
    """
    Fetch real-time emission factors from external API
    Falls back to local defaults if API fails
    """
    try:
        # API call with timeout
        url = "https://api.carboninterface.com/v1/emission_factors"
        headers = {'Authorization': 'Bearer YOUR_API_KEY'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return response.json()['emission_factor']
        else:
            return self._get_default_emission_factor(activity_type)
    except Exception as e:
        _logger.error(f"API fetch failed: {e}")
        return self._get_default_emission_factor(activity_type)
```

**Fallback Method:**
```python
def _get_default_emission_factor(self, activity_type):
    """Local emission factors as fallback"""
    return EMISSION_FACTORS.get(activity_type, 0)
```

**Onchange Integration:**
```python
@api.onchange('activity_type')
def _onchange_activity_type(self):
    if self.activity_type:
        self.emission_factor = self.fetch_emission_factor_from_api(self.activity_type)
```

**Scheduled Action:**
- Runs weekly
- Updates emission factors from API
- Logs success/failure

**Testing Criteria:**
- Emission factors auto-populate when creating activities
- System works offline (uses defaults)
- Scheduled action runs without errors
- API errors are logged properly

---

### STAGE 5: AI/ML Predictions
**Duration:** 2-3 hours  
**Priority:** MEDIUM-HIGH - Major innovation feature

**Files to Create:**
1. `wizards/__init__.py`
2. `wizards/carbon_prediction_wizard.py`
3. `wizards/carbon_prediction_wizard_views.xml`

**Wizard Model Definition:**
```python
class CarbonPredictionWizard(models.TransientModel):
    _name = 'carbon.prediction.wizard'
    _description = 'Carbon Emission Prediction'
    
    initiative_id = fields.Many2one('carbon.initiative', required=True)
    prediction_months = fields.Integer(default=3)
    predicted_co2 = fields.Float(readonly=True)
    trend = fields.Selection([
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining')
    ], readonly=True)
    recommendation = fields.Text(readonly=True)
```

**Core Prediction Algorithm:**
```python
def action_predict(self):
    """Simple linear regression prediction"""
    # 1. Get last 6 months of data
    # 2. Group by month and calculate savings
    # 3. Calculate average monthly savings
    # 4. Project forward: avg_monthly * prediction_months
    # 5. Determine trend (compare recent vs earlier)
    # 6. Generate recommendations based on patterns
```

**Recommendation Engine:**
```python
def _generate_recommendations(self, activities):
    """AI-driven recommendations"""
    recommendations = []
    
    # Analyze top emission sources
    type_counts = {}
    for activity in activities:
        type_counts[activity.activity_type] = type_counts.get(activity.activity_type, 0) + 1
    
    # Generate smart recommendations
    if 'electricity' in top_types:
        recommendations.append("🔋 Install solar panels or LED lighting")
    if 'fuel' in top_types:
        recommendations.append("🚗 Promote carpooling or EVs")
    
    return "\n".join(recommendations)
```

**Testing Criteria:**
- Wizard opens from initiative form
- Predictions are mathematically sound
- Trend analysis is accurate
- Recommendations are relevant

---

### STAGE 6: Demo Data & Polish
**Duration:** 1-2 hours  
**Priority:** CRITICAL - Required for demo

**Files to Create:**
1. `data/demo_data.xml` - Complete demo dataset

**Demo Data Requirements:**

**Initiatives (5-10):**
- Paperless Office Challenge
- Solar Energy Installation
- Sustainable Transport Program
- Waste Reduction Initiative
- Water Conservation Project

**Activities (50+):**
- Varied dates (last 6 months)
- All activity types represented
- Realistic quantities
- Mix of high and low impact activities

**Goals (10+):**
- Some achieved (100%+ achievement)
- Some in progress (50-99%)
- Some missed (date passed, <100%)
- Some pending (future date, 0%)

**Demo Data Structure:**
```xml
<odoo>
    <record id="initiative_paperless" model="carbon.initiative">
        <field name="name">Paperless Office Challenge 2025</field>
        <field name="category">waste</field>
        <field name="start_date">2025-01-01</field>
        <field name="end_date">2025-12-31</field>
        <field name="state">active</field>
        <field name="target_co2_reduction">1000</field>
        <field name="color">3</field>
    </record>
    
    <record id="activity_paper_01" model="carbon.activity">
        <field name="initiative_id" ref="initiative_paperless"/>
        <field name="activity_type">paper</field>
        <field name="activity_date">2025-01-05</field>
        <field name="quantity">500</field>
        <field name="unit">sheets</field>
        <field name="emission_factor">0.01</field>
        <field name="co2_saved">5</field>
    </record>
    
    <record id="goal_q1_paperless" model="carbon.goal">
        <field name="initiative_id" ref="initiative_paperless"/>
        <field name="name">Q1 2025 Paper Reduction</field>
        <field name="target_date">2025-03-31</field>
        <field name="target_co2_reduction">250</field>
        <field name="reward_points">500</field>
    </record>
</odoo>
```

**Testing Criteria:**
- All demo data loads without errors
- Relationships are correct
- Computed fields calculate properly
- Dashboard displays rich data
- Demo scenarios work end-to-end

---

## ODOO 19 CONVENTIONS & BEST PRACTICES

### Model Conventions
```python
# Naming
_name = "module.modelname"  # All lowercase, dot separator
_description = "Human Readable Name"
_order = "field_name desc"  # or "field_name asc"
_rec_name = "name"  # Field used for display (optional)

# Inheritance for chatter
_inherit = ['mail.thread', 'mail.activity.mixin']

# Field attributes
field_name = fields.Type(
    string="Label",
    required=True/False,
    readonly=True/False,
    tracking=True/False,  # For chatter
    help="Tooltip text",
    default=value,
    compute='_compute_method',
    store=True/False,
)

# Computed field decorator
@api.depends('field1', 'field2')
def _compute_field_name(self):
    for rec in self:
        rec.field_name = calculation

# Onchange decorator
@api.onchange('field_name')
def _onchange_field_name(self):
    # Update other fields based on change
    self.other_field = value

# Constraints
@api.constrains('field1', 'field2')
def _check_constraint(self):
    for rec in self:
        if condition:
            raise ValidationError(_('Error message'))
```

### View Conventions
```xml
<!-- Record ID format -->
<record id="view_model_viewtype" model="ir.ui.view">
    <!-- view_student_list, view_student_form, view_student_kanban -->

<!-- Widget types -->
<field name="status" widget="statusbar"/>
<field name="progress" widget="progressbar"/>
<field name="image" widget="image"/>
<field name="count" widget="statinfo"/>
<field name="selection" widget="badge"/>
<field name="boolean" widget="boolean_toggle"/>
<field name="tags" widget="many2many_tags"/>

<!-- Form structure -->
<form>
    <header>
        <button/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <div class="oe_button_box">
            <button class="oe_stat_button" icon="fa-icon">
                <field widget="statinfo"/>
            </button>
        </div>
        <group>
            <group>...</group>
            <group>...</group>
        </group>
        <notebook>
            <page>...</page>
        </notebook>
    </sheet>
    <chatter/>
</form>
```

### Security Conventions
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_model_user,access.model.user,model_module_modelname,,1,1,1,1
```

**Model ID format:** `model_module_modelname`  
Example: `model_carbon_initiative`

---

## INNOVATION FEATURES CHECKLIST

### External API Integration ✅
- [ ] API call method in carbon.activity
- [ ] Fallback to local defaults
- [ ] Error handling and logging
- [ ] Scheduled action for updates
- [ ] Works offline

### Dashboard & Analytics ✅
- [ ] Line chart (CO2 trend over time)
- [ ] Pie chart (emissions by category)
- [ ] Bar chart (initiative comparison)
- [ ] Pivot table (multi-dimensional)
- [ ] KPI summary cards
- [ ] Search panel with filters

### AI/ML Functionality ✅
- [ ] Prediction wizard
- [ ] Historical data analysis (6 months)
- [ ] Linear regression for forecasting
- [ ] Trend identification
- [ ] Pattern-based recommendations
- [ ] Anomaly detection (bonus)

### Workflow Automation ✅
- [ ] Computed fields update automatically
- [ ] Goal state auto-updates based on dates
- [ ] Scheduled actions (cron jobs)
- [ ] Email notifications (bonus)
- [ ] Chatter tracking on key fields

### Module Inheritance ✅
- [ ] Inherits mail.thread for chatter
- [ ] Links to res.users (employees)
- [ ] Can extend to HR module (department_id)
- [ ] Can link to project.project (bonus)

---

## DEMO SCRIPT (4 MINUTES)

**Sequence for presentation:**

1. **Opening (30s):** Introduce GreenTrack
2. **Dashboard (45s):** Show KPIs, charts, impact metrics
3. **Create Initiative (45s):** Add "Paperless Office" via Kanban
4. **Log Activities (30s):** Show auto-calculation, API integration
5. **AI Predictions (60s):** Run prediction wizard, show recommendations
6. **Impact Metrics (30s):** Trees saved, cars off road, SDG alignment
7. **Closing (20s):** Net Zero 2050 vision

**Key talking points:**
- Real-time tracking with API integration
- AI-powered predictions for planning
- Gamification for employee engagement
- Translates CO2 to real-world impact
- Ready for CSR reporting

---

## COMMON ISSUES & SOLUTIONS

### Installation Issues
**Problem:** Module won't install  
**Solution:** Check `__manifest__.py` syntax, verify all files exist

**Problem:** Missing dependencies  
**Solution:** Add required modules to `depends` list in manifest

### View Issues
**Problem:** Views not showing  
**Solution:** Verify XML syntax, check model name matches exactly

**Problem:** Fields not displaying  
**Solution:** Ensure field exists in model, check view mode compatibility

### Computed Field Issues
**Problem:** Computed fields not updating  
**Solution:** Check `@api.depends` has correct fields, ensure `store=True`

**Problem:** Circular dependency error  
**Solution:** Review depends chain, may need to split computation

### Relationship Issues
**Problem:** One2many not showing records  
**Solution:** Check inverse field name, verify foreign key

**Problem:** Many2one dropdown empty  
**Solution:** Check target model has records, verify access rights

### API Issues
**Problem:** API calls timing out  
**Solution:** Reduce timeout, improve error handling

**Problem:** API returns invalid data  
**Solution:** Add validation, use fallback defaults

---

## CODING STANDARDS

### Python
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to methods
- Use `_logger` for error logging
- Import `_` for translations: `from odoo import _`
- Handle exceptions gracefully

### XML
- Proper indentation (4 spaces)
- Close all tags
- Use meaningful IDs
- Add comments for complex sections
- Group related records

### Comments
```python
# Single-line explanation

"""
Multi-line docstring
explaining method purpose,
parameters, and return value
"""

# TODO: Feature to add later
# FIXME: Known issue to resolve
# NOTE: Important consideration
```

---

## TESTING CHECKLIST

### Functional Testing
- [ ] All models create/read/update/delete
- [ ] All computed fields calculate correctly
- [ ] All views render properly
- [ ] All relationships work
- [ ] Chatter tracks changes
- [ ] Search/filters work
- [ ] Smart buttons navigate correctly
- [ ] Kanban drag-and-drop works
- [ ] API integration functions
- [ ] Prediction wizard works
- [ ] Demo data loads completely

### Performance Testing
- [ ] App loads in <3 seconds
- [ ] Dashboard with 100+ records performs well
- [ ] No Python errors in logs
- [ ] No JavaScript console errors

### User Experience
- [ ] Navigation is intuitive
- [ ] Forms are easy to use
- [ ] Visual feedback is clear
- [ ] Error messages are helpful

---

## DELIVERABLES CHECKLIST

- [ ] Working Odoo module (ZIP or repository)
- [ ] All 3 models implemented
- [ ] All 3 view types (List, Form, Kanban)
- [ ] Dashboard with analytics
- [ ] Demo data populated (50+ activities)
- [ ] Security configuration (ir.model.access.csv)
- [ ] API integration working
- [ ] AI prediction feature working
- [ ] 3-5 minute demo prepared
- [ ] Module installs without errors

---

## EXECUTION TIMELINE

### Day 1 (8 hours)
- **9-11am:** Stage 1 - Models & setup
- **11am-2pm:** Stage 2 - Views
- **2-4pm:** Stage 3 - Dashboard
- **4-6pm:** Stage 4 - API

### Day 2 (8 hours)
- **9am-12pm:** Stage 5 - AI/ML
- **12-2pm:** Stage 6 - Demo data
- **2-4pm:** Polish & bug fixes
- **4-6pm:** Demo preparation

---

## HOW TO USE THIS CONTEXT

When working with Claude Code, you can:

1. **Request complete file implementations:**
   - "Create the complete carbon_initiative.py model file"
   - "Generate the carbon_initiative_views.xml with all views"

2. **Ask for specific stage guidance:**
   - "Help me implement Stage 1"
   - "What's next for Stage 3 dashboard?"

3. **Debug issues:**
   - "My computed field isn't updating, here's my code: ..."
   - "Getting XML syntax error, can you review this view?"

4. **Get best practices:**
   - "How should I structure the API error handling?"
   - "What's the best way to implement this computed field?"

5. **Request testing guidance:**
   - "How do I test the API integration?"
   - "What should I verify for Stage 2?"

---

## READY TO BUILD

You now have complete context for the GreenTrack project. Start by asking:

- "Let's begin with Stage 1 - create the __manifest__.py file"
- "Show me the complete carbon_initiative.py model"
- "I'm on Stage 3, help me build the dashboard views"
- "Review my code for [specific file]"

**Remember:** 
- Focus on one stage at a time
- Test after each stage before moving forward
- Use the demo data to validate functionality
- Keep the end demo in mind

**LET'S BUILD SOMETHING AMAZING! 🚀**