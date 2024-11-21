import { Component, OnInit } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  Validators,
  ReactiveFormsModule,
  AbstractControl,
  ValidationErrors,
  ValidatorFn,
  FormControl,
} from '@angular/forms';
import { AuthService } from '../auth.service';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatOptionModule } from '@angular/material/core';
import { passwordMatchValidator, passwordStrengthValidator } from 'src/app/shared/constant/data.constant';

@Component({
  selector: 'app-sign-up',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatCardModule,
    MatIconModule,
    MatFormFieldModule,
    MatOptionModule,
  ],
  templateUrl: './sign-up.component.html',
  styleUrls: ['./sign-up.component.scss'],
})
export class SignUpComponent implements OnInit {
  signUpForm!: FormGroup;
  errorMessage: string = '';
  hidePassword = true;
  submitted=false
  hideConfirmPassword = true;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.signUpForm = new FormGroup(
      {
        username: new FormControl(
          '',
          [
            Validators.required,
            Validators.minLength(3),
            Validators.maxLength(20),
            Validators.pattern('^[a-zA-Z0-9]+$'),
          ],
        ),
        email: new FormControl('', [Validators.required, Validators.email]),
        password: new FormControl('', [Validators.required, passwordStrengthValidator()]),
        confirmPassword: new FormControl('',Validators.required),
        name: new FormControl('',Validators.required),
        age: new FormControl('',[Validators.min(18),Validators.required]),
        gender: new FormControl('',Validators.required),
        placeOfResidence: new FormControl (''),
        fieldOfStudy: new FormControl(''),
      },
      { validators: passwordMatchValidator }
    );
  }


  onSubmit() {
    this.submitted = true
    console.log(this.signUpForm.controls,'before valid value')

    if (this.signUpForm.valid) {
      console.log(this.signUpForm.controls,'value')
      const formValue = { ...this.signUpForm.value };
      delete formValue.confirmPassword;

      this.authService.signUp(formValue).subscribe({
        next: (response) => {
          console.log('User registered successfully', response);
          localStorage.setItem('access_token', response.access_token);
          this.router.navigate(['/dashboard']);
        },
        error: (error) => {
          console.error('Error registering user', error);
          if (error.status === 409) {
            this.errorMessage =
              'A user with this username or email already exists.';
          } else {
            this.errorMessage = error.error.message || 'Failed to register user.';
          }
        },
      });
    } else {
      this.errorMessage = 'Please correct the errors in the form.';
    }
  }
}


