! ***********************************************************************
!
!   Copyright (C) 2010  The MESA Team
!
!   This program is free software: you can redistribute it and/or modify
!   it under the terms of the GNU Lesser General Public License
!   as published by the Free Software Foundation,
!   either version 3 of the License, or (at your option) any later version.
!
!   This program is distributed in the hope that it will be useful,
!   but WITHOUT ANY WARRANTY; without even the implied warranty of
!   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
!   See the GNU Lesser General Public License for more details.
!
!   You should have received a copy of the GNU Lesser General Public License
!   along with this program. If not, see <https://www.gnu.org/licenses/>.
!
! ***********************************************************************

      module run_star_extras

      use star_lib
      use star_def
      use const_def
      use math_lib
      use auto_diff

      implicit none


      contains



      subroutine extras_controls(id, ierr)
         integer, intent(in) :: id
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         s% extras_startup => extras_startup
         s% extras_check_model => extras_check_model
         s% extras_finish_step => extras_finish_step
         s% extras_after_evolve => extras_after_evolve
         s% how_many_extra_history_columns => how_many_extra_history_columns
         s% data_for_extra_history_columns => data_for_extra_history_columns
         s% how_many_extra_profile_columns => how_many_extra_profile_columns
         s% data_for_extra_profile_columns => data_for_extra_profile_columns
         s% pg% TRho_pgstar_decorator => TRho_reference_lines
      end subroutine extras_controls

      subroutine TRho_reference_lines(id, xmin, xmax, ymin, ymax, plot_num, ierr)
         use pgstar_support, only: hydrogen_burn_logRho, hydrogen_burn_logT, &
            helium_burn_logRho, helium_burn_logT, carbon_burn_logRho, carbon_burn_logT, &
            oxygen_burn_logRho, oxygen_burn_logT, gamma_4_thirds_logRho, gamma_4_thirds_logT, &
            Line_Type_Dash, Line_Type_Solid
         use pgstar_colors, only: clr_Gray, clr_Gold
         integer, intent(in) :: id, plot_num
         real, intent(in) :: xmin, xmax, ymin, ymax
         integer, intent(out) :: ierr
         real :: x(2), y(2)

         ierr = 0
         call pgsave
         call pgsci(clr_Gray)
         call pgsls(Line_Type_Dash)
         call pgslw(1)

         ! Same approximate gas/radiation pressure boundary as TRho_Profile.
         ! The built-in TRho plot already draws the electron degeneracy line.
         x = [xmin, xmax]
         y = real(log10(3.2d7)) + (x - real(log10(0.7d0)))/3.0
         call reference_curve(x, y, 'P\drad\u = P\dgas\u')
         call reference_curve(hydrogen_burn_logRho, hydrogen_burn_logT, 'H burn')
         call reference_curve(helium_burn_logRho, helium_burn_logT, 'He burn')
         call reference_curve(carbon_burn_logRho, carbon_burn_logT, 'C burn')
         call reference_curve(oxygen_burn_logRho, oxygen_burn_logT, 'O burn')

         call pgsci(clr_Gold)
         call pgsls(Line_Type_Solid)
         call reference_curve(gamma_4_thirds_logRho, gamma_4_thirds_logT, '\(0529)\d1\u = 4/3')
         call pgunsa

      contains

         subroutine reference_curve(logRho, logT, label)
            real, intent(in) :: logRho(:), logT(:)
            character(len=*), intent(in) :: label
            integer :: k
            real :: fraction, label_x, label_y, char_height

            call pgline(size(logRho), logRho, logT)
            ! Put the label on a visible segment, even when the history axes
            ! show only a small part of a reference curve.
            do k = size(logRho)-1, 1, -1
               label_x = max(min(logRho(k), logRho(k+1)), xmin + 0.08*(xmax-xmin))
               label_x = min(label_x, xmax - 0.25*(xmax-xmin))
               if (label_x < min(logRho(k), logRho(k+1)) .or. &
                   label_x > max(logRho(k), logRho(k+1))) cycle
               if (logRho(k+1) == logRho(k)) cycle
               fraction = (label_x-logRho(k))/(logRho(k+1)-logRho(k))
               label_y = logT(k) + fraction*(logT(k+1)-logT(k))
               if (label_y <= ymin + 0.04*(ymax-ymin) .or. &
                   label_y >= ymax - 0.08*(ymax-ymin)) cycle
               call pgqch(char_height)
               call pgsch(0.55*char_height)
               call pgptxt(label_x, label_y + 0.02*(ymax-ymin), 0.0, 0.0, label)
               call pgsch(char_height)
               exit
            end do
         end subroutine reference_curve

      end subroutine TRho_reference_lines

      subroutine extras_startup(id, restart, ierr)
         integer, intent(in) :: id
         logical, intent(in) :: restart
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         !if (.not. restart) s% op_split_burn = .true. ! first timestep on mod start.
      end subroutine extras_startup


      subroutine extras_after_evolve(id, ierr)
         integer, intent(in) :: id
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         include 'formats'
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
      end subroutine extras_after_evolve


      ! returns either keep_going, retry, or terminate.
      integer function extras_check_model(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         extras_check_model = keep_going
      end function extras_check_model


      integer function how_many_extra_history_columns(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         how_many_extra_history_columns = 0
      end function how_many_extra_history_columns


      subroutine data_for_extra_history_columns(id, n, names, vals, ierr)
         integer, intent(in) :: id, n
         character (len=maxlen_history_column_name) :: names(n)
         real(dp) :: vals(n)
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
      end subroutine data_for_extra_history_columns


      integer function how_many_extra_profile_columns(id)
         use star_def, only: star_info
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         how_many_extra_profile_columns = 1
      end function how_many_extra_profile_columns


      subroutine data_for_extra_profile_columns(id, n, nz, names, vals, ierr)
         use star_def, only: star_info, maxlen_profile_column_name
         use const_def, only: dp
         integer, intent(in) :: id, n, nz
         character (len=maxlen_profile_column_name) :: names(n)
         real(dp) :: vals(nz,n)
         integer, intent(out) :: ierr
         type (star_info), pointer :: s
         integer :: k
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         names(1) = 'zbar_div_abar'
         do k=1,s% nz
            vals(k,1) = s% zbar(k)/s% abar(k)
         end do
      end subroutine data_for_extra_profile_columns

      ! returns either keep_going or terminate.
      integer function extras_finish_step(id)
         integer, intent(in) :: id
         integer :: ierr
         type (star_info), pointer :: s
         ierr = 0
         call star_ptr(id, s, ierr)
         if (ierr /= 0) return
         !s% op_split_burn = .false.

         if (log10(s%T(s%nz)) > 9.5d0 .and. .not. s% op_split_burn) then
            s% gold_tol_residual_norm3 = 1d-5 ! default = 1d-6
            s% gold_tol_max_residual3 = 5d-3 ! default is 1d-4
         else
            s% gold_tol_residual_norm3 = 1d-6 ! default = 1d-6
            s% gold_tol_max_residual3 = 1d-4 ! default is 1d-4
         end if
         extras_finish_step = keep_going
         if (.not. s% x_logical_ctrl(37)) return
         if (extras_finish_step == terminate) &
             s% termination_code = t_extras_finish_step
      end function extras_finish_step

      end module run_star_extras

