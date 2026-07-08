using AIAugmentedPitchAnalyzer.Application.DTOs.Auth;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IServices;
using AIAugmentedPitchAnalyzer.Application.Interfaces.IRepository;
using AIAugmentedPitchAnalyzer.Domain.Entities;
using System.Threading.Tasks;
using System;
using Microsoft.EntityFrameworkCore;
using AIAugmentedPitchAnalyzer.Persistence.Context;

namespace AIAugmentedPitchAnalyzer.Infrastructure.Services
{
    /// <summary>
    /// Basic auth service scaffold. Password hashing and JWT are not implemented here yet.
    /// This service will be expanded in Module 4 to include secure password hashing and JWT generation.
    /// </summary>
    public class AuthService : IAuthService
    {
        private readonly IUserRepository _userRepository;
        private readonly ApplicationDbContext _context;
        private readonly ITokenService _tokenService;

        public AuthService(IUserRepository userRepository, ApplicationDbContext context, ITokenService tokenService)
        {
            _userRepository = userRepository;
            _context = context;
            _tokenService = tokenService;
        }

        public async Task<AuthResponse> RegisterAsync(RegisterRequest request)
        {
            // NOTE: Placeholder implementation. Password hashing and duplicate checks will be added in Module 4.
            // prevent duplicate email
            var existing = await _userRepository.GetByEmailAsync(request.Email);
            if (existing != null) throw new InvalidOperationException("Email already registered");

            var user = new User
            {
                FirstName = request.FirstName,
                LastName = request.LastName,
                Email = request.Email,
                PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.Password),
                RoleId = Guid.Empty // will set default role later
            };
            // ensure default founder role exists
            var role = await _context.Roles.FirstOrDefaultAsync(r => r.Name == "Founder");
            if (role == null)
            {
                role = new Role { Name = "Founder", Description = "Default founder role" };
                _context.Roles.Add(role);
                await _context.SaveChangesAsync();
            }

            user.RoleId = role.Id;

            await _userRepository.AddAsync(user);
            await _context.SaveChangesAsync();

            var token = _tokenService.GenerateToken(user);

            return new AuthResponse { Email = user.Email, FirstName = user.FirstName, Token = token };
        }

        public async Task<AuthResponse?> LoginAsync(LoginRequest request)
        {
            var user = await _userRepository.GetByEmailAsync(request.Email);
            if (user == null) return null;

            if (!BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash)) return null;

            var token = _tokenService.GenerateToken(user);

            return new AuthResponse { Email = user.Email, FirstName = user.FirstName, Token = token };
        }
    }
}
