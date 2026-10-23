from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import StudentProfile, Scholarship
from decimal import Decimal
# =========================
# REGISTER
# =========================

def register(request):

    if request.method == "POST":
        

        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "register.html", {
                "error": "Passwords do not match."
            })

        if not email:
            return render(request, "register.html", {
                "error": "Email is required."
            })

        if User.objects.filter(username=email).exists():
            return render(request, "register.html", {
                "error": "Email already registered."
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name
        )

        user.save()

        return render(request, "register.html", {
            "success": "Registration successful!"
        })

    return render(request, "register.html")


# =========================
# LOGIN
# =========================

def user_login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            login(request, user)
            profile = StudentProfile.objects.filter(user=user).first()
               
            return render(request, "studentprofile.html", {
                "profile": profile
            })
           

        else:

            return render(request, "login.html", {
                "error": "Invalid email or password."
            })

   
    # This handles GET request
    return render(request, "login.html")
# =========================
# SCHOLARSHIP ELIGIBILITY
# =========================
def get_eligible_scholarships(profile):

    scholarships = Scholarship.objects.all()
    eligible = []

    print("TOTAL SCHOLARSHIPS =", scholarships.count())

    # Student education level
    student_level = ""

    if profile.education_level:
        student_level = profile.education_level.lower().strip()

    for scholarship in scholarships:

        print(
            "CHECKING:",
            scholarship.name,
            "| Category:", scholarship.category,
            "| Max Income:", scholarship.maximum_income,
            "| Min %:", scholarship.minimum_percentage,
            "| Education:", scholarship.education_level
        )

        # -------------------------
        # Category check
        # -------------------------
        if scholarship.category:
            if profile.category and profile.category.lower() not in scholarship.category.lower():
                continue

        # -------------------------
        # Income check
        # -------------------------
        if scholarship.maximum_income:
            if profile.annual_income and profile.annual_income > scholarship.maximum_income:
                continue

        # -------------------------
        # Percentage check
        # -------------------------
        if scholarship.minimum_percentage:
            if profile.percentage_cgpa and profile.percentage_cgpa < scholarship.minimum_percentage:
                continue

        # -------------------------
        # Education level check
        # -------------------------
        if scholarship.education_level and student_level:

            scholarship_level = scholarship.education_level.lower().strip()

            # Undergraduate
            if student_level == "undergraduate":

                if scholarship_level not in [
                    "undergraduate",
                    "ug",
                    "post-matric",
                    "post-matric scholarship",
                    "ug/pg",
                    "professional ug/pg",
                    "after 12th / ug",
                    "diploma/degree/pg"
                ]:
                    continue

            # Postgraduate
            elif student_level == "postgraduate":

                if scholarship_level not in [
                    "postgraduate",
                    "pg",
                    "post-matric",
                    "post-matric scholarship",
                    "ug/pg",
                    "pg/research",
                    "professional ug/pg",
                    "diploma/degree/pg"
                ]:
                    continue

            # 12th
            elif student_level == "12th":

                if "11th & 12th" not in scholarship_level:
                    continue

            # Diploma
            elif student_level == "diploma":

                if scholarship_level not in [
                    "diploma",
                    "diploma/degree/pg",
                    "post-matric"
                ]:
                    continue

        # -------------------------
        # Eligible scholarship
        # -------------------------
        eligible.append(scholarship)

        print("ELIGIBLE:", scholarship.name)

    print("TOTAL ELIGIBLE =", len(eligible))

    return eligible

def calculate_match_score(profile, scholarship):

    score = 0

    # -------------------------
    # Category Match - 30 points
    # -------------------------
    if scholarship.category and profile.category:

        student_category = profile.category.lower().strip()
        scholarship_category = scholarship.category.lower().strip()

        if student_category == scholarship_category:
            score += 30

        elif student_category in scholarship_category:
            score += 30

    # -------------------------
    # Income Match - 25 points
    # -------------------------
    if scholarship.maximum_income and profile.annual_income:

        if profile.annual_income <= scholarship.maximum_income:
            score += 25

    # -------------------------
    # Education Level Match - 20 points
    # -------------------------
    if scholarship.education_level and profile.education_level:

        student_level = profile.education_level.lower().strip()
        scholarship_level = scholarship.education_level.lower().strip()

        education_match = False

        if student_level == "undergraduate":

            if scholarship_level in [
                "undergraduate",
                "ug",
                "post-matric",
                "post-matric scholarship",
                "ug/pg",
                "professional ug/pg",
                "after 12th / ug",
                "diploma/degree/pg"
            ]:
                education_match = True

        elif student_level == "postgraduate":

            if scholarship_level in [
                "postgraduate",
                "pg",
                "post-matric",
                "post-matric scholarship",
                "ug/pg",
                "pg/research",
                "professional ug/pg",
                "diploma/degree/pg"
            ]:
                education_match = True

        elif student_level == "12th":

            if "11th & 12th" in scholarship_level:
                education_match = True

        elif student_level == "diploma":

            if scholarship_level in [
                "diploma",
                "diploma/degree/pg",
                "post-matric"
            ]:
                education_match = True

        if education_match:
            score += 20

    # -------------------------
    # Academic Score - 15 points
    # -------------------------
    if scholarship.minimum_percentage:

        if profile.percentage_cgpa:

            if profile.percentage_cgpa >= scholarship.minimum_percentage:
                score += 15

    # -------------------------
    # State Match - 10 points
    # -------------------------
    if scholarship.state and profile.state:

        if (
            scholarship.state.lower().strip() == "maharashtra"
            and profile.state.lower().strip() == "maharashtra"
        ):
            score += 10

    return score



def get_scholarship_reasons(profile, scholarship):

    reasons = []

    # Category
    if scholarship.category:
        reasons.append(
            f"Category: {profile.category} ✓"
        )

    # Income
    if scholarship.maximum_income:
        if profile.annual_income:
            reasons.append(
                f"Family Income: ₹{profile.annual_income} — within limit ✓"
            )

    # Education
    if scholarship.education_level:
        reasons.append(
            f"Education Level: {profile.education_level} ✓"
        )

    # Academic Score
    if scholarship.minimum_percentage:
        if profile.percentage_cgpa:
            reasons.append(
                f"Academic Score: {profile.percentage_cgpa}% — meets requirement ✓"
            )

    return reasons
def scholarships(request):

    profile = StudentProfile.objects.filter(
        user=request.user
    ).first()

    if not profile:
        return redirect("student_profile")

    eligible_scholarships = get_eligible_scholarships(profile)

    # प्रत्येक scholarship साठी reasons आणि match score तयार करणे
    for scholarship in eligible_scholarships:

        scholarship.reasons = get_scholarship_reasons(
            profile,
            scholarship
        )

        scholarship.match_score = calculate_match_score(
            profile,
            scholarship
        )
        print("MATCH SCORE:", scholarship.name, "=", scholarship.match_score)

    # Highest match score first
    eligible_scholarships.sort(
        key=lambda scholarship: scholarship.match_score,
        reverse=True
    )

    return render(request, "scholarships.html", {
        "profile": profile,
        "eligible_scholarships": eligible_scholarships
    })   
    

  

def student_profile(request):

    if request.method == "POST":
       
        dob = request.POST.get("dob")
       
        if not dob:
            return render(request, "studentprofile.html",{
                "error": "please enter your Date of Birth."
            })
        profile = StudentProfile.objects.filter(user=request.user).first()
        if profile is None:
            profile = StudentProfile(user=request.user)
          
        profile.full_name=request.POST.get("full_name")
        profile.dob=dob
        profile.gender=request.POST.get("gender")
        profile.mobile=request.POST.get("mobile")
        profile.email=request.POST.get("email")
        profile.state=request.POST.get("state")
        profile.district=request.POST.get("district")
        profile.taluka=request.POST.get("taluka")
        profile.city_village=request.POST.get("city_village")
        profile.pincode=request.POST.get("pincode")

        profile.education_level=request.POST.get("education_level")
        profile.course_name=request.POST.get("course_name")
        profile.university_board=request.POST.get("university_board")
        profile.college=request.POST.get("college")
        profile.current_year=request.POST.get("current_year")
        percentage_value = request.POST.get("percentage_cgpa")
        percentage_type = request.POST.get("percentage_type")

        print("PERCENTAGE VALUE =", percentage_value)
        print("PERCENTAGE TYPE =", percentage_type)

        if not percentage_type:
          return render(request, "studentprofile.html", {
           "error": "Please select Percentage or CGPA.",
               "profile": profile
        })

        if not percentage_value:
           return render(request, "studentprofile.html", {
            "error": "Please enter your Percentage/CGPA.",
            "profile": profile
        })

        if percentage_type == "Percentage":
          percentage_value = float(percentage_value)

        elif percentage_type == "CGPA":
          percentage_value = float(percentage_value) * 9.5

        profile.percentage_cgpa = percentage_value
        profile.percentage_type = percentage_type
        
       
        profile.admission_type=request.POST.get("admission_type")
        print("ADMISSION TYPE =", request.POST.get("admission_type"))
        print("POST DATA =", request.POST)
        
        income = request.POST.get("annual_income")

        if income:
         profile.annual_income = Decimal(income)
        else:
         profile.annual_income = None
        profile.category=request.POST.get("category")
        profile.parent_occupation=request.POST.get("parent_occupation")
        profile.family_members=request.POST.get("family_members")
        print("DISABILITY STATUS =", request.POST.get("disability_status"))
        profile.residence_type=request.POST.get("residence_type")
        profile.domicile_state=request.POST.get("domicile_state")

        profile.scholarship_type=request.POST.get("scholarship_type")
        profile.save()
        

       
    
        return redirect("scholarships")

def home(request):
    return render(request, 'index.html')

    