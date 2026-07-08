using AIAugmentedPitchAnalyzer.Application.Interfaces.IRepository;
using AIAugmentedPitchAnalyzer.Domain.Entities;
using AIAugmentedPitchAnalyzer.Persistence.Context;
using Microsoft.EntityFrameworkCore;
using System.Threading.Tasks;

namespace AIAugmentedPitchAnalyzer.Persistence.Repositories
{
    public class UserRepository : GenericRepository<User>, IUserRepository
    {
        public UserRepository(ApplicationDbContext context) : base(context)
        {
        }

        public async Task<User?> GetByEmailAsync(string email)
        {
            return await _dbSet.AsNoTracking().Include(u => u.Role).FirstOrDefaultAsync(x => x.Email == email);
        }
    }
}
